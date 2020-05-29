import base64
import datetime
import decimal
import json

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Field, TextField, QuerySet, ManyToOneRel, ManyToManyField, ForeignKey
import django.db.models.options as options
from django.db.models.base import ModelBase
from django.db.models.fields.files import FieldFile, ImageFieldFile

from django.apps import apps
from pictures.for_es import es_client

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('es_index_name', 'es_indexes')


class EsTextField(TextField):
    es_index = {}

    def __init__(self, *args, **kwargs):
        if kwargs.keys().__contains__("es_index"):
            self.es_index = kwargs.pop('es_index')
        super(EsTextField, self).__init__(*args, **kwargs)


class EsForeignKey(ForeignKey):
    es_index = {}

    def __init__(self, *args, **kwargs):
        if kwargs.keys().__contains__("es_index"):
            self.es_index = kwargs.pop('es_index')
        super(EsForeignKey, self).__init__(*args, **kwargs)


def get_model_from_name(name):
    ct = ContentType.objects.get(model=name)
    return ct.model_class()


class EsfModel(Model):
    class Meta:
        abstract = True
        es_index_name = ""
        es_indexes = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.ComplexEncoder = None

    def obj2es(self, index_name):
        self._meta.es_index_name = index_name
        json_obj = json.dumps(self.repr_json(), cls=self.ComplexEncoder)
        return json_obj

    def repr_json(self):
        d = {}
        fields = self._meta.get_fields()
        for field in fields:
            if hasattr(field, "es_index"):
                indexes = field.es_index
                m = indexes.get(self._meta.es_index_name)
                if m is not None:
                    if not isinstance(field, ManyToOneRel):
                        if not isinstance(field, ManyToManyField):
                            o = getattr(self, field.name)
                            if hasattr(o, "_meta") and hasattr(o._meta, "es_index_name"):
                                o._meta.es_index_name = self._meta.es_index_name
                            if isinstance(o, (datetime.date, datetime.datetime)):
                                o = o.isoformat()
                            if isinstance(o, memoryview):
                                o = str(base64.encodebytes(o))
                            if isinstance(o, (
                                    datetime.timedelta, datetime.time, decimal.Decimal, FieldFile, ImageFieldFile)):
                                o = str(o)
                        else:
                            print("loh")
                            o = field.related_model.objects.all()
                            for el in o:
                                if hasattr(el._meta, "es_index_name"):
                                    o._meta.es_index_name = self._meta.es_index_name
                        d.update({str(field.name): o})
        return d

    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, EsfModel):
                return EsfModel.repr_json(obj)
            else:
                if isinstance(obj, QuerySet):
                    return [EsfModel.repr_json(r)
                            for r in obj]
                else:
                    return json.JSONEncoder.default(self, obj)

    @classmethod
    def mod2es(cls, obj, index_name):
        obj._meta.es_index_name = index_name
        json_obj = json.dumps(obj.repr_mapp(obj), cls=obj.Complex1Encoder)
        return json_obj

    @classmethod
    def repr_mapp(cls, obj):
        if hasattr(obj, "_meta") and hasattr(obj._meta, "es_index_name"):
            d = {}
            fields = obj._meta.get_fields()
            for field in fields:
                if hasattr(field, "es_index"):
                    indexes = field.es_index
                    m = indexes.get(obj._meta.es_index_name)
                    if m is not None:
                        if not isinstance(field, ManyToOneRel):
                            if field.related_model is not None:
                                ml = field.related_model
                                m.update({"properties": ml})
                                if hasattr(ml._meta, "es_index_name"):
                                    ml._meta.es_index_name = obj._meta.es_index_name
                            d.update({str(field.name): m})
        else:
            d = obj
        return d

    class Complex1Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, ModelBase) and hasattr(obj, "_meta"):
                return EsfModel.repr_mapp(obj)
            if isinstance(obj, dict):
                return EsfModel.repr_mapp(obj)
            return json.JSONEncoder.default(self, obj)

    @staticmethod
    def create_indices_for_model(model, with_mapping):
        es = es_client(['localhost'])
        res = []
        if hasattr(model, "_meta") and hasattr(model._meta, "es_indexes"):
            es_ind = model._meta.es_indexes
            for ind in es_ind:
                index_name = ind.get('index_name')
                doc_type = ind.get('doc_type')
                if index_name is not None and doc_type is not None and index_name != "" and doc_type != "":
                    if es.indices.exists(index=index_name):
                        es.indices.delete(index=index_name)
                    es.indices.create(index=index_name)
                    if with_mapping:
                        mapp = model.mod2es(model, index_name)
                        body = '{"properties": ' + mapp + '}'
                        es.indices.put_mapping(index=index_name,
                                               doc_type=doc_type,
                                               body=body,
                                               include_type_name=True,
                                               )

    @staticmethod
    def create_indices(with_mapping):
        for model in apps.get_app_config('pictures').get_models():
            EsfModel.create_indices_for_model(model, with_mapping)

    @staticmethod
    def put_document(obj):
        es = es_client(['localhost'])
        res = []
        obj_model = obj._meta.model
        if hasattr(obj, "_meta") and hasattr(obj._meta, "es_indexes"):
            es_ind = obj_model._meta.es_indexes
            for ind in es_ind:
                index_name = ind.get('index_name')
                doc_type = ind.get('doc_type')
                if index_name is not None and doc_type is not None and index_name != "" and doc_type != "":
                    json_obj = obj.obj2es(index_name)
                    res.append(es.index(index=index_name, doc_type=doc_type, body=json_obj, id=obj.id))
        return res

    @staticmethod
    def put_documents():
        res = []
        for model in apps.get_app_config('pictures').get_models():
            for obj in model.objects.all():
                res.append(EsfModel.put_document(obj))
        return res
