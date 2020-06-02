import base64
import datetime
import decimal
import json
import logging

from django.db.models import Model, ManyToManyField, QuerySet

from django.db.models import ManyToOneRel
from django.contrib.contenttypes.models import ContentType
import django.db.models.options as options
from django.db.models.base import ModelBase
from django.apps import apps
from django.db.models.fields.files import FieldFile, ImageFieldFile
from elasticsearch import Elasticsearch

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('es_mapping', 'es_path', 'mappings')
logging.basicConfig(filename="log-file.log", level=logging.INFO)


def get_model_from_name(name):
    ct = ContentType.objects.get(model=name)
    return ct.model_class()


def connect_es():
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    try:
        if _es.ping():
            logging.info('Connect ES')
            return _es
        else:
            logging.error('Cannot connect ES')
            raise SystemExit
    except Exception:
        logging.error('Error')
        raise SystemExit


class EsModel(Model):
    class Meta:
        abstract = True
        es_mapping = {}
        es_path = ""
        mappings = []

    @classmethod
    def get_mappings(cls):
        return cls._meta.mappings

    @classmethod
    def get_es_mapping(cls):
        return cls._meta.es_mapping

    @classmethod
    def set_es_mapping(cls, es_mapping):
        cls._meta.es_mapping = es_mapping

    @classmethod
    def get_es_path(cls):
        return cls._meta.es_path

    @classmethod
    def set_es_path(cls, es_path):
        cls._meta.es_path = es_path

    @classmethod
    def get_model_name(cls):
        return str(cls._meta.model_name)

    def obj2es(self):
        self.set_es_path(self.get_model_name() + ".")
        json_obj = json.dumps(self.repr_json(), cls=self.ComplexEncoder)
        return json_obj

    def repr_json(self):
        d = {}
        model_start = get_model_from_name(self.get_es_path().partition('.')[0])
        if hasattr(model_start._meta, "es_mapping"):
            mapping = model_start.get_es_mapping()
            fields = self._meta.get_fields()
            for key in mapping:
                mapping_field = mapping[key]
                for field in fields:
                    if key == self.get_es_path() + field.name:
                        if mapping_field is not None:
                            if not isinstance(field, ManyToOneRel):
                                if not isinstance(field, ManyToManyField):
                                    o = getattr(self, field.name)
                                    if hasattr(o, "_meta") and hasattr(o._meta, "es_path"):
                                        o.set_es_path(self.get_es_path() + field.name + ".")
                                    if isinstance(o, (datetime.date, datetime.datetime)):
                                        o = o.isoformat()
                                    if isinstance(o, memoryview):
                                        o = str(base64.encodebytes(o))
                                    if isinstance(o, (
                                            datetime.timedelta, datetime.time, decimal.Decimal, FieldFile,
                                            ImageFieldFile)):
                                        o = str(o)
                                else:
                                    o = field.related_model.objects.all()
                                    for el in o:
                                        if hasattr(el._meta, "es_path"):
                                            el.set_es_path(self.get_es_path() + field.name + ".")
                                d.update({str(field.name): o})
        return d

    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, EsModel):
                return EsModel.repr_json(obj)
            else:
                if isinstance(obj, QuerySet):
                    return [EsModel.repr_json(r)
                            for r in obj]
                else:
                    return json.JSONEncoder.default(self, obj)

    @classmethod
    def mod2es(cls, obj):
        obj.set_es_path(obj.get_model_name() + ".")
        json_obj = json.dumps(obj.repr_mapp(obj), cls=obj.Complex1Encoder)
        return json_obj

    @classmethod
    def repr_mapp(cls, obj):
        if hasattr(obj, "_meta") and hasattr(obj._meta, "es_path"):
            d = {}
            model_start = get_model_from_name(obj.get_es_path().partition('.')[0])
            if hasattr(model_start._meta, "es_mapping"):
                mapping_es = model_start.get_es_mapping()
                fields = obj._meta.get_fields()
                for key in mapping_es:
                    mapping_field = mapping_es[key]
                    for field in fields:
                        if key == obj.get_es_path() + field.name:
                            if mapping_field is not None:
                                if not isinstance(field, ManyToOneRel):
                                    if field.related_model is not None:
                                        ml = field.related_model
                                        mapping_field.update({"properties": ml})
                                        if hasattr(ml._meta, "es_path"):
                                            ml.set_es_path(obj.get_es_path() + field.name + ".")
                                    d.update({str(field.name): mapping_field})
        else:
            d = obj
        return d

    class Complex1Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, ModelBase) and hasattr(obj, "_meta"):
                return EsModel.repr_mapp(obj)
            if isinstance(obj, dict):
                return EsModel.repr_mapp(obj)
            return json.JSONEncoder.default(self, obj)

    @staticmethod
    def create_indices_for_model(model, with_mapping, es):
        if hasattr(model, "_meta") and hasattr(model._meta, "mappings"):
            mappings = model.get_mappings()
            for m in mappings:
                index_name = m.get('es_index_name')
                doc_type = m.get('es_doc_type')
                if index_name is not None and doc_type is not None and index_name != "" and doc_type != "":
                    if es.indices.exists(index=index_name):
                        es.indices.delete(index=index_name)
                    es.indices.create(index=index_name)
                    if with_mapping:
                        model._meta.es_mapping = m.get("es_mapping")
                        mapp = model.mod2es(model)
                        body = '{"properties": ' + mapp + '}'
                        es.indices.put_mapping(index=index_name,
                                               doc_type=doc_type,
                                               body=body,
                                               include_type_name=True,
                                               )

    @staticmethod
    def create_indices(with_mapping):
        es = connect_es()
        res = []
        for model in apps.get_models():
            if hasattr(model, "_meta") and hasattr(model._meta, "mappings"):
                EsModel.create_indices_for_model(model, with_mapping, es)
                for obj in model.objects.all():
                    res.append(EsModel.put_document(obj, es))
        return res

    @staticmethod
    def put_document(obj, es):
        res = []
        obj_model = obj._meta.model
        if hasattr(obj_model, "_meta") and hasattr(obj_model._meta, "mappings"):
            mappings = obj_model.get_mappings()
            for m in mappings:
                index_name = m.get('es_index_name')
                doc_type = m.get('es_doc_type')
                if index_name is not None and doc_type is not None and index_name != "" and doc_type != "":
                    obj_model._meta.es_mapping = m.get("es_mapping")
                    json_obj = obj.obj2es()
                    res.append(es.index(index=index_name, doc_type=doc_type, body=json_obj, id=obj.id))
        return res
