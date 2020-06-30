import base64, datetime, decimal, json, logging, collections

from django.conf import settings
from django.db.models import Model, ManyToManyField, QuerySet, ManyToOneRel

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

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('es_mapping', 'es_path', 'mappings',
                                                 'es_index_name', 'es_doc_type', 'index_using_fields')
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


# {'host': 'localhost', 'port': 9200}
def connect_es(connection_es):
    _es = Elasticsearch([connection_es])
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


es = connect_es(getattr(settings, 'CONNECTION_ES'))


class DjesModel(Model):
    class Meta:
        abstract = True
        mappings = []
        index_using_fields = False

        es_mapping = collections.OrderedDict()
        es_path = ""

    @classmethod
    def get_mappings(cls):
        return cls._meta.mappings

    @classmethod
    def set_mappings(cls, mappings):
        cls._meta.mappings = mappings

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
    def get_index_using_fields(cls):
        return cls._meta.index_using_fields

    @classmethod
    def set_index_using_fields(cls, index_using_fields):
        cls._meta.index_using_fields = index_using_fields

    #
    @classmethod
    def get_model_name(cls):
        return str(cls._meta.model_name)

    def obj2es(self):
        self.set_es_path(self.get_model_name() + ".")
        json_obj = json.dumps(self.repr_json(), cls=self.ComplexEncoder)
        return json_obj

    def modify_obj(self, field):
        if not isinstance(field, ManyToManyField):
            o = getattr(self, field.name)
            if hasattr(o, "_meta") and hasattr(o._meta, "es_path"):
                o.set_es_path(self.get_es_path() + field.name + ".")
            if isinstance(o, (datetime.date, datetime.datetime)):
                o = o.isoformat()
            if isinstance(o, memoryview):
                o = str(base64.encodebytes(o))
            if isinstance(o, (
                    datetime.timedelta, datetime.time, decimal.Decimal, FieldFile, ImageFieldFile)):
                o = str(o)
        else:
            o = field.related_model.objects.all()
            for el in o:
                if hasattr(el._meta, "es_path"):
                    el.set_es_path(self.get_es_path() + field.name + ".")
        return o

    def dict_from_es_mapping(self, es_mapping):
        d = {}
        fields = self._meta.get_fields()
        for key in es_mapping:
            mapping_field = es_mapping[key]
            for field in fields:
                if key == self.get_es_path() + field.name:
                    if mapping_field is not None:
                        # if not isinstance(field, ManyToOneRel):
                        o = self.modify_obj(field)
                        d.update({str(field.name): o})

        return d

    def dict_from_fields(self):
        d = {}
        fields = self._meta.get_fields()
        for field in fields:
            if hasattr(field, "es_index"):
                index_flag = field.es_index
                if index_flag is True:
                    # if not isinstance(field, ManyToOneRel):
                    o = self.modify_obj(field)
                    d.update({str(field.name): o})
        return d

    def repr_json(self):
        d = {}
        model_start = get_model_from_name(self.get_es_path().partition('.')[0])
        if hasattr(model_start._meta, "index_using_fields"):
            index_using_fields = model_start.get_index_using_fields()
            if index_using_fields:
                d = self.dict_from_fields()
            else:
                if hasattr(model_start._meta, "es_mapping"):
                    es_mapping = model_start.get_es_mapping().copy()
                    d = self.dict_from_es_mapping(es_mapping)
        return d

    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, DjesModel):
                return DjesModel.repr_json(obj)
            else:
                if isinstance(obj, QuerySet):
                    return [DjesModel.repr_json(r)
                            for r in obj]
                else:
                    return json.JSONEncoder.default(self, obj)

    @classmethod
    def mod2es(cls, obj):
        obj.set_es_path(obj.get_model_name() + ".")
        json_obj = json.dumps(obj.repr_mapp(obj), cls=obj.Complex1Encoder)
        return json_obj

    @classmethod
    def modify_mapp(cls, obj, field, mapping_field):
        # if not isinstance(field, ManyToOneRel):
        if field.related_model is not None:
            ml = field.related_model
            mapping_field.update({"properties": ml})
            if hasattr(ml._meta, "es_path"):
                ml.set_es_path(obj.get_es_path() + field.name + ".")
        return mapping_field

    @classmethod
    def map_dict_from_es_mapping(cls, obj, es_mapping):
        d = {}
        fields = obj._meta.get_fields()
        for key in es_mapping:
            mapping_field = es_mapping[key].copy()
            for field in fields:
                if key == obj.get_es_path() + field.name:
                    if mapping_field is not None:
                        mapping_field = cls.modify_mapp(obj, field, mapping_field)
                        d.update({str(field.name): mapping_field})
        return d

    @classmethod
    def map_dict_from_fields(cls, obj):
        d = {}
        fields = obj._meta.get_fields()
        for field in fields:
            if hasattr(field, "es_index") and hasattr(field, "es_map"):
                index_flag = field.es_index
                if index_flag is True:
                    mapping_field = field.es_map
                    mapping_field = cls.modify_mapp(obj, field, mapping_field)
                    d.update({str(field.name): mapping_field})
        return d

    @classmethod
    def repr_mapp(cls, obj):
        d = {}
        if hasattr(obj, "_meta") and hasattr(obj._meta, "es_path"):
            model_start = get_model_from_name(obj.get_es_path().partition('.')[0])
            if hasattr(model_start._meta, "index_using_fields"):
                index_using_fields = model_start.get_index_using_fields()
                if index_using_fields:
                    d = cls.map_dict_from_fields(obj)
                else:
                    if hasattr(model_start._meta, "es_mapping"):
                        es_mapping = model_start.get_es_mapping().copy()
                        d = cls.map_dict_from_es_mapping(obj, es_mapping)
        else:
            d = obj
        return d

    class Complex1Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, ModelBase) and hasattr(obj, "_meta"):
                return DjesModel.repr_mapp(obj)
            if isinstance(obj, dict):
                return DjesModel.repr_mapp(obj)
            return json.JSONEncoder.default(self, obj)

    @staticmethod
    def del_document(obj, es):
        res = []
        obj_model = obj._meta.model
        if hasattr(obj_model, "_meta") and hasattr(obj_model._meta, "mappings"):
            mappings = obj_model.get_mappings()
            for m in mappings:
                index_name = m.get('es_index_name')
                doc_type = m.get('es_doc_type')
                if index_name is not None and doc_type is not None and index_name != "" and doc_type != "":
                    res.append(es.delete(index=index_name, doc_type=doc_type, id=obj.id))
        return res

    @staticmethod
    def create_indices_for_model(model, with_mapping, es):
        if hasattr(model, "_meta") and hasattr(model._meta, "mappings"):
            mappings = model.get_mappings()
            for m in mappings:
                index_name = m.get('es_index_name')
                doc_type = m.get('es_doc_type')
                # model.set_es_index_name(index_name)
                # model.set_es_doc_type(doc_type)
                em = m.get("es_mapping")
                if em is not None:
                    model.set_es_mapping(m.get("es_mapping").copy())
                else:
                    model.set_es_mapping(collections.OrderedDict())
                if index_name is not None and doc_type is not None and index_name != "" and doc_type != "":
                    try:
                        if es.indices.exists(index=index_name):
                            es.indices.delete(index=index_name)
                            logging.info("Index %s deleted", index_name)
                        es.indices.create(index=index_name)
                    except Exception:
                        logging.info("Error")
                    now = datetime.datetime.now()
                    logging.info("Index %s created, time: %s", index_name, now.isoformat())

                if with_mapping:
                    mapp = model.mod2es(model)
                    body = '{"properties": ' + mapp + '}'
                    try:
                        es.indices.put_mapping(index=index_name,
                                               doc_type=doc_type,
                                               body=body,
                                               include_type_name=True,
                                               )
                        now = datetime.datetime.now()
                        logging.info("Mapping added, time: %s", now.isoformat())
                    except Exception:
                        logging.info("Error with model %s", model._meta.model_name)

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
                    em = m.get("es_mapping")
                    if em is not None:
                        obj_model.set_es_mapping(em.copy())
                    else:
                        obj_model.set_es_mapping(collections.OrderedDict())
                    json_obj = obj.obj2es()
                    try:
                        res.append(es.index(index=index_name, doc_type=doc_type, body=json_obj, id=obj.id))
                        now = datetime.datetime.now()
                        logging.info("The document id = %i is put on the ES, time: %s", obj.id, now.isoformat())
                    except Exception:
                        logging.warning("Error. Cannot put document on the ES")
        return res

    @staticmethod
    def create_indices(with_mapping):
        res = []
        for model in apps.get_models():
            if hasattr(model, "_meta") and hasattr(model._meta, "mappings"):
                DjesModel.create_indices_for_model(model, with_mapping, es)
                for obj in model.objects.all():
                    res.append(DjesModel.put_document(obj, es))
        return res

    @receiver(post_save)
    def es_save(sender, instance, **kwargs):
        if isinstance(sender, DjesModel) and hasattr(sender, "_meta") and hasattr(sender._meta, "es_mapping"):
            sender.put_document(instance, es)

    @receiver(post_delete)
    def es_delete(sender, instance, **kwargs):
        if isinstance(sender, DjesModel) and hasattr(sender, "_meta") and hasattr(sender._meta, "es_mapping"):
            sender.del_document(instance, es)
