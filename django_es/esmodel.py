import base64, datetime, decimal, json, logging, collections
from django.db.models import Model, ManyToManyField, QuerySet, ManyToOneRel

from django.contrib.contenttypes.models import ContentType
import django.db.models.options as options
from django.db.models.base import ModelBase
from django.apps import apps
from django.db.models.fields.files import FieldFile, ImageFieldFile
from elasticsearch import Elasticsearch

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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


es = connect_es()


class EsModel(Model):
    class Meta:
        abstract = True
        es_mapping = collections.OrderedDict()
        es_path = ""
        mappings = []

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
                mapping_es = model_start.get_es_mapping().copy()
                fields = obj._meta.get_fields()
                for key in mapping_es:
                    mapping_field = mapping_es[key].copy()
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
    def create_indices_for_model(model, with_mapping, with_deletion, es):
        if hasattr(model, "_meta") and hasattr(model._meta, "mappings"):
            mappings = model.get_mappings()
            for m in mappings:
                index_name = m.get('es_index_name')
                doc_type = m.get('es_doc_type')
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
                        model.set_es_mapping(m.get("es_mapping").copy())
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
    def create_indices(with_mapping, with_deletion):
        res = []
        for model in apps.get_models():
            if hasattr(model, "_meta") and hasattr(model._meta, "mappings"):
                EsModel.create_indices_for_model(model, with_mapping, with_deletion, es)
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
                    obj_model.set_es_mapping(m.get("es_mapping").copy())
                    json_obj = obj.obj2es()
                    try:
                        res.append(es.index(index=index_name, doc_type=doc_type, body=json_obj, id=obj.id))
                        logging.info("The document id = %i is put on the ES", obj.id)
                    except Exception:
                        logging.warning("Error !!! Cannot put document on the ES")
        return res


@receiver(post_save)
def es_save(sender, instance, **kwargs):
    if isinstance(sender, EsModel) and hasattr(sender, "_meta") and hasattr(sender._meta, "es_mapping"):
        sender.put_document(instance, es)


@receiver(post_delete)
def es_delete(sender, instance, **kwargs):
    sender.del_document(instance, es)
