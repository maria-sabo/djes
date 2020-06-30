import uuid

from django.db import models
from django.db.models import Model, TextField, ForeignKey
from django_elasticsearch.managers import ElasticsearchManager

from django_es.esmodel import EsModel
from django_es_f.esfmodel import EsfModel
# from django_es_f.esfmodel import EsfModel, EsTextField, EsForeignKey, EsBigIntegerField, \
#     EsBinaryField, EsBooleanField, EsCharField, EsDateField, EsDateTimeField, EsDecimalField, EsDurationField, \
#     EsEmailField, EsFilePathField, EsFloatField, EsIntegerField, EsUUIDField, EsURLField, EsTimeField, \
#     EsSmallIntegerField, EsSlugField, EsPositiveSmallIntegerField, EsPositiveIntegerField, EsNullBooleanField, \
#     EsFileField, EsImageField, EsGenericIPAddressField, EsOneToOneField, EsManyToManyField

from dj_es.djesmodel import DjesModel, EsTextField, EsForeignKey, EsBigIntegerField, \
    EsBinaryField, EsBooleanField, EsCharField, EsDateField, EsDateTimeField, EsDecimalField, EsDurationField, \
    EsEmailField, EsFilePathField, EsFloatField, EsIntegerField, EsUUIDField, EsURLField, EsTimeField, \
    EsSmallIntegerField, EsSlugField, EsPositiveSmallIntegerField, EsPositiveIntegerField, EsNullBooleanField, \
    EsFileField, EsImageField, EsGenericIPAddressField, EsOneToOneField, EsManyToManyField

from django_elasticsearch.models import EsIndexable

from django_elasticsearch import managers


class TestFk(DjesModel):
    text = EsTextField(es_index=True, es_map={'type': 'text'})
    # text = TextField()


class TestModel(DjesModel):
    name = EsTextField(es_index=True, )
    fk = EsForeignKey(TestFk, on_delete=models.CASCADE, null=True, blank=True, default=None,
                      es_index=True, es_map={'type': 'object'})

    # name = TextField()
    # fk = ForeignKey(TestFk, on_delete=models.CASCADE, null=True, blank=True, default=None,)

    class Meta:
        index_using_fields = False
        mappings = [
            {
                "es_index_name": "i_test",
                "es_doc_type": "t_test",
                "es_mapping": {
                    "testmodel.name": {'type': 'text'},
                    "testmodel.fk": {'type': 'object'},
                    "testmodel.fk.text": {'type': 'text'},
                },
            },
            {
                "es_index_name": "ii_test",
                "es_doc_type": "tt_test",
                "es_mapping": {
                    "testmodel.name": {'type': 'date'},
                },
            },
        ]


class Author2(DjesModel):
    name = EsTextField(es_index=True, es_map={'type': 'keyword'})
    date_birth = EsDateField(es_index=True, es_map={'type': 'text'})
    date_death = EsDateField(es_index=True, es_map={'type': 'text'})
    country_birth = EsTextField(es_index=True, es_map={'type': 'text'})
    note = EsCharField(default='', max_length=10000, es_index=True, es_map={'type': 'text'})

    # рассмотрение всех полей

    field_big_int = EsBigIntegerField(null=True, blank=True, default=None,
                                      es_index=True, es_map={'type': 'long'})
    field_bin = EsBinaryField(null=True, blank=True, default=None,
                              es_index=True, es_map={'type': 'binary'})
    field_null_boolean = EsNullBooleanField(null=True, blank=True, default=None,
                                            es_index=True, es_map={'type': 'boolean'})
    field_datetime = EsDateTimeField(null=True, blank=True, default=None,
                                     es_index=True, es_map={'type': 'date'})
    field_decimal = EsDecimalField(null=True, blank=True, default=None, max_digits=10, decimal_places=2,
                                   es_index=True, es_map={'type': 'float'})
    field_duration = EsDurationField(null=True, blank=True, default=None,
                                     es_index=True, es_map={'type': 'text'})
    field_email = EsEmailField(null=True, blank=True, default=None,
                               es_index=True, es_map={'type': 'text'})
    field_file = EsFileField(default=None, blank=True, null=True, es_index=True, es_map={'type': 'text'})
    field_filepath = EsFilePathField(null=True, blank=True, default=None,
                                     es_index=True, es_map={'type': 'text'})
    field_float = EsFloatField(null=True, blank=True, default=None,
                               es_index=True, es_map={'type': 'float'})
    field_image = EsImageField(default=None, blank=True, null=True,
                               es_index=True, es_map={'type': 'text'})
    field_generic_ip = EsGenericIPAddressField(default=None, blank=True, null=True,
                                               es_index=True, es_map={'type': 'text'})
    field_positive_int = EsPositiveIntegerField(null=True, blank=True, default=None,
                                                es_index=True, es_map={'type': 'integer'})
    field_positive_small_int = EsPositiveSmallIntegerField(null=True, blank=True, default=None,
                                                           es_index=True, es_map={'type': 'short'})
    field_slug = EsSlugField(null=True, blank=True, default=None, es_index=True, es_map={'type': 'text'})
    field_small_int = EsSmallIntegerField(null=True, blank=True, default=None,
                                          es_index=True, es_map={'type': 'short'})
    field_time = EsTimeField(null=True, blank=True, default=None, es_index=True, es_map={'type': 'text'})
    field_url = EsURLField(null=True, blank=True, default=None, es_index=True, es_map={'type': 'text'})
    field_uuid = EsUUIDField(null=True, blank=True, default=uuid.uuid4, editable=False,
                             es_index=True, es_map={'type': 'text'})

    class Meta:
        index_using_fields = True
        mappings = [{"es_index_name": "index_with_new_fields2",
                     "es_doc_type": "type_with_new_fields2"}]


class Author(DjesModel):
    name = models.TextField()
    date_birth = models.DateField()
    date_death = models.DateField()
    country_birth = models.TextField()
    note = models.CharField(default='', max_length=10000)

    # рассмотрение всех полей

    field_big_int = models.BigIntegerField(null=True, blank=True, default=None)
    field_bin = models.BinaryField(null=True, blank=True, default=None)
    field_null_boolean = models.NullBooleanField(null=True, blank=True, default=None)
    field_datetime = models.DateTimeField(null=True, blank=True, default=None)
    field_decimal = models.DecimalField(null=True, blank=True, default=None, max_digits=10, decimal_places=2)
    field_duration = models.DurationField(null=True, blank=True, default=None)
    field_email = models.EmailField(null=True, blank=True, default=None)
    field_file = models.FileField(default=None, blank=True, null=True)
    field_filepath = models.FilePathField(null=True, blank=True, default=None)
    field_float = models.FloatField(null=True, blank=True, default=None)
    field_image = models.ImageField(default=None, blank=True, null=True)
    field_generic_ip = models.GenericIPAddressField(default=None, blank=True, null=True)
    field_positive_int = models.PositiveIntegerField(null=True, blank=True, default=None)
    field_positive_small_int = models.PositiveSmallIntegerField(null=True, blank=True, default=None)
    field_slug = models.SlugField(null=True, blank=True, default=None)
    field_small_int = models.SmallIntegerField(null=True, blank=True, default=None)
    field_time = models.TimeField(null=True, blank=True, default=None)
    field_url = models.URLField(null=True, blank=True, default=None)
    field_uuid = models.UUIDField(null=True, blank=True, default=uuid.uuid4, editable=False)

    class Meta:
        index_using_fields = False
        mappings = [
            {
                "es_index_name": "i_author",
                "es_doc_type": "t_author",
                "es_mapping": {
                    "author.name": {"type": "keyword"},
                    "author.country_birth": {"type": "text"},
                    "author.date_birth": {"type": "text"},
                    "author.date_death": {"type": "text"},
                    "author.note": {"type": "text"},
                },
            },
            {
                "es_index_name": "index_with_new_fields",
                "es_doc_type": "type_with_new_fields",
                "es_mapping": {
                    "author.field_big_int": {"type": "long"},
                    "author.field_bin": {"type": "binary"},
                    "author.field_null_boolean": {"type": "boolean"},
                    "author.field_datetime": {"type": "date"},
                    "author.field_decimal": {"type": "float"},
                    "author.field_duration": {"type": "text"},
                    "author.field_email": {"type": "text"},
                    "author.field_filepath": {"type": "text"},
                    "author.field_float": {"type": "float"},
                    "author.field_generic_ip": {"type": "text"},
                    "author.field_positive_int": {"type": "integer"},
                    "author.field_positive_small_int": {"type": "short"},
                    "author.field_slug": {"type": "text"},
                    "author.field_small_int": {"type": "short"},
                    "author.field_time": {"type": "text"},
                    "author.field_url": {"type": "text"},
                    "author.field_uuid": {"type": "text"},
                    "author.field_file": {"type": "text"},
                    "author.field_image": {"type": "text"},
                },
            }
        ]


class Address2(DjesModel):
    country = EsTextField()
    city = EsTextField()
    street = EsTextField()
    house = EsTextField()


class Address(DjesModel):
    country = models.TextField()
    city = models.TextField()
    street = models.TextField()
    house = models.TextField()


class Person2(DjesModel):
    name = EsTextField(es_index=True, es_map={'type': 'text'})
    address = EsForeignKey(Address2, on_delete=models.CASCADE, null=True, blank=True, default=None,
                           es_index=True, es_map={'type': 'object'})

    class Meta:
        index_using_fields = True
        mappings = [{"es_index_name": "i_person2",
                     "es_doc_type": "t_person2"}]


class Person(DjesModel):
    name = models.TextField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, default=None)

    class Meta:
        index_using_fields = False
        mappings = [
            {
                "es_index_name": "i_person",
                "es_doc_type": "t_person",
                "es_mapping": {
                    "person.name": {'type': 'text'},
                    "person.address": {'type': 'object'},
                    "person.address.country": {'type': 'text'},
                    "person.address.city": {'type': 'text'},
                    "person.address.street": {'type': 'text'},
                    "person.address.house": {'type': 'text'},
                },
            },
            {
                "es_index_name": "ii_person",
                "es_doc_type": "tt_person",
                "es_mapping": {
                    "person.name": {'type': 'text'},
                },
            },
        ]


class Museum2(DjesModel):
    name = EsTextField(es_index=True)
    address = EsForeignKey(Address2, on_delete=models.CASCADE, null=True, blank=True, default=None,
                           es_index=True, es_map={'type': 'object'})
    year_foundation = EsIntegerField(es_index=True, es_map={'type': 'integer'})
    note = EsTextField(default='', es_index=True, es_map={'type': 'text'})
    persona = EsOneToOneField(Person2, on_delete=models.CASCADE, null=True, blank=True, default=None,
                              es_index=True, es_map={'type': 'object'})

    class Meta:
        index_using_fields = True
        mappings = [{"es_index_name": "i_museum2",
                     "es_doc_type": "t_museum2"}]


class Museum(DjesModel):
    name = models.TextField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, default=None)
    year_foundation = models.IntegerField()
    note = models.TextField(default='')
    persona = models.OneToOneField(Person, on_delete=models.CASCADE, null=True, blank=True, default=None)

    class Meta:
        index_using_fields = False
        mappings = [
            {
                "es_index_name": "i_museum",
                "es_doc_type": "t_museum",
                "es_mapping": {
                    "museum.name": {"type": "text"},
                    "museum.year_foundation": {"type": "integer"},
                    "museum.note": {'type': 'text'},
                    "museum.persona": {'type': 'object'},
                    "museum.persona.name": {'type': 'text'},
                    "museum.address": {'type': 'object'},
                    "museum.address.country": {'type': 'text'},
                    "museum.address.city": {'type': 'text'},
                    "museum.address.street": {'type': 'text'},
                    "museum.address.house": {'type': 'text'},
                },
            },
            {
                "es_index_name": "ii_museum",
                "es_doc_type": "tt_museum",
                "es_mapping": {
                    "museum.name": {"type": "text"},
                    "museum.year_foundation": {"type": "integer"},
                    "museum.note": {'type': 'text'},
                },
            },
        ]


class Picture2(DjesModel):
    name = EsTextField(es_index=True, es_map={'type': 'text'})
    auth = EsForeignKey(Author2, on_delete=models.CASCADE, es_index=True, es_map={'type': 'object'})
    museum = EsForeignKey(Museum2, on_delete=models.CASCADE, es_index=True, es_map={'type': 'object'})
    persons = EsManyToManyField(Person2, null=True, blank=True, default=None,
                                es_index=True, es_map={'type': 'object'})
    note = EsTextField(default='', es_index=True, es_map={'type': 'text'})
    addr = EsForeignKey(Address2, on_delete=models.CASCADE, null=True, blank=True, default=None,
                        es_index=True, es_map={'type': 'object'})

    class Meta:
        index_using_fields = True
        mappings = [{"es_index_name": "i_picture2",
                     "es_doc_type": "t_picture2"}]


class Picture(DjesModel):
    name = models.TextField()
    auth = models.ForeignKey(Author, on_delete=models.CASCADE)
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE)
    persons = models.ManyToManyField(Person, null=True, blank=True, default=None)
    note = models.TextField(default='')
    addr = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, default=None)

    class Meta:
        index_using_fields = False
        mappings = [
            {"es_index_name": "i_picture",
             "es_doc_type": "t_picture",
             "es_mapping": {
                 "picture.name": {"type": "text"},
                 "picture.note": {"type": "text"},
                 "picture.auth": {"type": "object"},
                 "picture.auth.name": {"type": "text"},
                 "picture.auth.country_birth": {"type": "text"},

                 "picture.addr": {"type": "object"},
                 "picture.addr.country": {"type": "text"},
                 "picture.addr.city": {"type": "text"},
                 "picture.addr.street": {"type": "text"},
                 "picture.addr.house": {"type": "text"},

                 "picture.persons": {"type": "object"},
                 "picture.persons.name": {"type": "text"},
                 "picture.persons.address": {"type": "object"},
                 "picture.persons.address.country": {"type": "text"},

                 "picture.museum": {"type": "object"},
                 "picture.museum.name": {"type": "text"},
                 "picture.museum.address": {"type": "object"},
                 "picture.museum.address.country": {"type": "text"},
                 "picture.museum.address.street": {"type": "text"}, "picture.museum.persona": {"type": "object"},
                 "picture.museum.persona.name": {"type": "text"},
                 "picture.museum.persona.address": {"type": "object"},
                 "picture.museum.persona.address.country": {"type": "text"},
                 "picture.museum.persona.address.city": {"type": "text"},
             },
             }
        ]


class TestAFk(DjesModel):
    text = TextField()


class TestAModel(DjesModel):
    name = TextField()
    fk = ForeignKey(TestFk, on_delete=models.CASCADE, null=True, blank=True, default=None)
    # em = ElasticsearchManager()
    #
    # class es(EsIndexable.Elasticsearch):
    #     fields = ['name', 'fk']
    #     mappings = {'name': {'type': 'text'},
    #                 'fk': {'type': 'object'}}

    # class El(EsIndexable.Elasticsearch):
    #     index = 'TA'
    #     doc_type = 'TA'
    #     fields = {'fk'}


class TestBFk(DjesModel):
    text = TextField()


class TestBModel(DjesModel):
    name = TextField()
    fk = ForeignKey(TestFk, on_delete=models.CASCADE, null=True, blank=True, default=None)
