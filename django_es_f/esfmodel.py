import base64
import datetime
import decimal
import json
import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model, Field, TextField, QuerySet, ManyToOneRel, ManyToManyField, ForeignKey, \
    BigIntegerField, BinaryField, BooleanField, CharField, DateField, DateTimeField, DecimalField, DurationField, \
    EmailField, FilePathField, FloatField, IntegerField, UUIDField, URLField, TimeField, SmallIntegerField, SlugField, \
    PositiveSmallIntegerField, PositiveIntegerField, NullBooleanField, FileField, ImageField, GenericIPAddressField, \
    OneToOneField
import django.db.models.options as options
from django.db.models.base import ModelBase

from django.apps import apps
from django.db.models.fields.files import FieldFile, ImageFieldFile
from elasticsearch import Elasticsearch

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('es_index_name', 'es_doc_type')

logging.basicConfig(filename="log-file.log", level=logging.INFO)


class EsField:
    es_index = True
    es_map = {}

    def __init__(self, *args, **kwargs):
        if kwargs.keys().__contains__('es_index'):
            self.es_index = kwargs.pop('es_index')
        if kwargs.keys().__contains__('es_map'):
            self.es_map = kwargs.pop('es_map')
        super(EsField, self).__init__(*args, **kwargs)


class EsTextField(EsField, TextField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsBigIntegerField(EsField, BigIntegerField):
    es_map = {"type": "long"}


class EsBinaryField(EsField, BinaryField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsBooleanField(EsField, BooleanField):
    es_map = {"type": "boolean"}


class EsCharField(EsField, CharField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsDateField(EsField, DateField):
    es_map = {"type": "date"}


class EsDateTimeField(EsField, DateTimeField):
    es_map = {"type": "date"}


class EsDecimalField(EsField, DecimalField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsDurationField(EsField, DurationField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsEmailField(EsField, EmailField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsFileField(EsField, FileField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsFilePathField(EsField, FilePathField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsFloatField(EsField, FloatField):
    es_map = {"type": "float"}


class EsImageField(EsField, ImageField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsIntegerField(EsField, IntegerField):
    es_map = {"type": "long"}


class EsNullBooleanField(EsField, NullBooleanField):
    es_map = {"type": "boolean"}


class EsPositiveIntegerField(EsField, PositiveIntegerField):
    es_map = {"type": "long"}


class EsPositiveSmallIntegerField(EsField, PositiveSmallIntegerField):
    es_map = {"type": "long"}


class EsSlugField(EsField, SlugField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsSmallIntegerField(EsField, SmallIntegerField):
    es_map = {"type": "long"}


class EsTimeField(EsField, TimeField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsURLField(EsField, URLField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsUUIDField(EsField, UUIDField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsGenericIPAddressField(EsField, GenericIPAddressField):
    es_map = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}


class EsForeignKey(EsField, ForeignKey):
    es_map = {"type": "object"}


class EsOneToOneField(EsField, OneToOneField):
    es_map = {"type": "object"}


class EsManyToManyField(EsField, ManyToManyField):
    es_map = {"type": "object"}


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


class EsfModel(Model):
    class Meta:
        abstract = True
        es_index_name = ""
        es_doc_type = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_es_index_name(cls):
        return cls._meta.es_index_name

    @classmethod
    def set_es_index_name(cls, es_index_name):
        cls._meta.es_index_name = es_index_name

    @classmethod
    def get_es_doc_type(cls):
        return cls._meta.es_doc_type

    @classmethod
    def set_es_doc_type(cls, es_doc_type):
        cls._meta.es_doc_type = es_doc_type

    def obj2es(self):
        json_obj = json.dumps(self.repr_json(), cls=self.ComplexEncoder)
        return json_obj

    def repr_json(self):
        d = {}
        fields = self._meta.get_fields()
        for field in fields:
            if hasattr(field, "es_index"):
                index_flag = field.es_index
                if index_flag is True:
                    if not isinstance(field, ManyToOneRel):
                        if not isinstance(field, ManyToManyField):
                            o = getattr(self, field.name)
                            if isinstance(o, (datetime.date, datetime.datetime)):
                                o = o.isoformat()
                            if isinstance(o, memoryview):
                                o = str(base64.encodebytes(o))
                            if isinstance(o, (
                                    datetime.timedelta, datetime.time, decimal.Decimal, FieldFile, ImageFieldFile)):
                                o = str(o)
                        else:
                            o = field.related_model.objects.all()
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
    def mod2es(cls, obj):
        json_obj = json.dumps(obj.repr_mapp(obj), cls=obj.Complex1Encoder)
        return json_obj

    @classmethod
    def repr_mapp(cls, obj):
        if hasattr(obj, "_meta") and hasattr(obj._meta, "es_index_name"):
            d = {}
            fields = obj._meta.get_fields()
            for field in fields:
                if hasattr(field, "es_index") and hasattr(field, "es_map"):
                    index_flag = field.es_index
                    m = field.es_map
                    if index_flag is True:
                        if not isinstance(field, ManyToOneRel):
                            if field.related_model is not None:
                                ml = field.related_model
                                m.update({"properties": ml})
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
    def create_indices_for_model(model, with_mapping, with_deletion, es):
        if hasattr(model, "_meta") and hasattr(model._meta, "es_index_name") and hasattr(model._meta, "es_doc_type"):
            index_name = model._meta.es_index_name
            doc_type = model._meta.es_doc_type
            if index_name is not None and doc_type is not None and index_name != "" and doc_type != "":
                new = False
                if with_deletion:
                    if es.indices.exists(index=index_name):
                        es.indices.delete(index=index_name)
                        logging.info("Index %s deleted", index_name)
                    es.indices.create(index=index_name)
                    new = True
                    logging.info("Index %s created", index_name)
                else:
                    if not es.indices.exists(index=index_name):
                        es.indices.create(index=index_name)
                        new = True
                        logging.info("Index %s created", index_name)
                if with_mapping and new:
                    mapp = model.mod2es(model)
                    body = '{"properties": ' + mapp + '}'
                    try:
                        es.indices.put_mapping(index=index_name,
                                               doc_type=doc_type,
                                               body=body,
                                               include_type_name=True,
                                               )
                        logging.info("Mapping added")
                    except Exception:
                        logging.info("Error with model %s", model._meta.model_name)

    @staticmethod
    def put_document(obj, es):
        res = []
        obj_model = obj._meta.model
        if hasattr(obj, "_meta") and hasattr(obj._meta, "es_index_name") and hasattr(obj._meta, "es_doc_type"):
            index_name = obj_model._meta.es_index_name
            doc_type = obj_model._meta.es_doc_type
            if index_name is not None and doc_type is not None and index_name != "" and doc_type != "":
                json_obj = obj.obj2es()
                try:
                    res.append(es.index(index=index_name, doc_type=doc_type, body=json_obj, id=obj.id))
                    logging.info("The document id = %i is put on the ES", obj.id)
                except Exception:
                    logging.warning("Error !!! Cannot put document on the ES")
        return res

    @staticmethod
    def create_indices(with_mapping, with_deletion):
        es = connect_es()
        res = []
        for model in apps.get_models():
            if hasattr(model, "_meta") and hasattr(model._meta, "es_index_name") and hasattr(model._meta,
                                                                                             "es_doc_type"):
                EsfModel.create_indices_for_model(model, with_mapping,  with_deletion, es)
                for obj in model.objects.all():
                    res.append(EsfModel.put_document(obj, es))
        return res
