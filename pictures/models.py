import uuid

from django.db import models
from django.db.models import Model

from es_model.esmodel import EsModel
from esf_model.esfmodel import EsfModel, EsTextField, EsForeignKey


class TestFk(EsfModel):
    text = EsTextField(es_index={"index1": {"type": "keyword"}, "index2": {"type": "keyword"}})

    # class Meta:
    #     es_indexes = [{"index_name": "index1", "doc_type": "doctype1"},
    #                   {"index_name": "index2", "doc_type": "doctype2"}]


class TestModel(EsfModel):
    name = EsTextField(es_index={"index1": {"type": "text"}})
    fk = EsForeignKey(TestFk, on_delete=models.CASCADE, null=True, blank=True, default=None,
                      es_index={"index1": {"type": "object"}})

    class Meta:
        es_indexes = [{"index_name": "index1", "doc_type": "doctype1"},
                      {"index_name": "index2", "doc_type": "doctype2"}]


class Author(EsModel):
    name = models.TextField()
    date_birth = models.DateField()
    date_death = models.DateField()
    country_birth = models.TextField()
    note = models.CharField(default='', max_length=10000)

    # рассмотрение всех полей

    field_bigInt = models.BigIntegerField(null=True, blank=True, default=None)
    field_bin = models.BinaryField(null=True, blank=True, default=None)
    field_nullBoolean = models.NullBooleanField(null=True, blank=True, default=None)
    field_datetime = models.DateTimeField(null=True, blank=True, default=None)
    field_decimal = models.DecimalField(null=True, blank=True, default=None, max_digits=10, decimal_places=2)
    field_duration = models.DurationField(null=True, blank=True, default=None)
    field_email = models.EmailField(null=True, blank=True, default=None)
    field_file = models.FileField(default=None, blank=True, null=True)
    field_filepath = models.FilePathField(null=True, blank=True, default=None)
    field_float = models.FloatField(null=True, blank=True, default=None)
    field_image = models.ImageField(default=None, blank=True, null=True)
    field_genericIP = models.GenericIPAddressField(default=None, blank=True, null=True)
    field_positiveInt = models.PositiveIntegerField(null=True, blank=True, default=None)
    field_positiveSmallInt = models.PositiveSmallIntegerField(null=True, blank=True, default=None)
    field_slug = models.SlugField(null=True, blank=True, default=None)
    field_smallInt = models.SmallIntegerField(null=True, blank=True, default=None)
    field_time = models.TimeField(null=True, blank=True, default=None)
    field_url = models.URLField(null=True, blank=True, default=None)
    field_uuid = models.UUIDField(null=True, blank=True, default=uuid.uuid4, editable=False)

    class Meta:
        mappings = [
            {
                "es_index_name": "i_author",
                "es_doc_type": "t_author",
                "es_mapping": {
                    "author.name": {"type": "keyword"},
                    "author.country_birth": {"type": "text"},
                    # "author.date_birth": {"type": "text", "format": "YYYY:MM"},
                    "author.date_death": {"type": "text"},
                    "author.note": {"type": "text"},
                },
            },
            {
                "es_index_name": "index_with_new_fields",
                "es_doc_type": "type_with_new_fields",
                "es_mapping": {
                    "author.field_bigInt": {"type": "long"},
                    "author.field_bin": {"type": "binary"},
                    "author.field_nullBoolean": {"type": "boolean"},
                    "author.field_datetime": {"type": "date", "format": "year"},
                    "author.field_decimal": {"type": "float"},
                    "author.field_duration": {"type": "text"},
                    "author.field_email": {"type": "text"},
                    "author.field_filepath": {"type": "text"},
                    "author.field_float": {"type": "float"},
                    "author.field_genericIP": {"type": "text"},
                    "author.field_positiveInt": {"type": "integer"},
                    "author.field_positiveSmallInt": {"type": "short"},
                    "author.field_slug": {"type": "text"},
                    "author.field_smallInt": {"type": "short"},
                    "author.field_time": {"type": "text"},
                    "author.field_url": {"type": "text"},
                    "author.field_uuid": {"type": "text"},
                    "author.field_file": {"type": "text"},
                    "author.field_image": {"type": "text"},
                },
            }
        ]


class Address(EsModel):
    country = models.TextField()
    city = models.TextField()
    street = models.TextField()
    house = models.TextField()


class Person(EsModel):
    name = models.TextField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, default=None)

    class Meta:
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


class Museum(EsModel):
    name = models.TextField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, default=None)
    year_foundation = models.IntegerField()
    note = models.TextField(default='')
    persona = models.OneToOneField(Person, on_delete=models.CASCADE, null=True, blank=True, default=None)

    class Meta:
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


class Picture(EsModel):
    name = models.TextField()
    auth = models.ForeignKey(Author, on_delete=models.CASCADE)
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE)
    persons = models.ManyToManyField(Person, null=True, blank=True, default=None)
    note = models.TextField(default='')
    addr = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, default=None)

    class Meta:
        mappings = [
            {"es_index_name": "i_picture",
             "es_doc_type": "t_picture",
             "es_mapping": {
                 "picture.name": {'type': "text"},
                 "picture.note": {'type': 'text'},
                 "picture.auth": {'type': 'object'},
                 "picture.auth.name": {'type': 'text', "store": True},
                 "picture.auth.country_birth": {'type': 'text'},

                 "picture.addr": {"type": "object"},
                 "picture.addr.country": {"type": "text"},
                 "picture.addr.city": {"type": "text"},
                 "picture.addr.street": {"type": "text"},
                 "picture.addr.house": {"type": "text"},

                 "picture.persons": {'type': 'object'},
                 "picture.persons.name": {'type': 'text'},
                 "picture.persons.address": {'type': 'object'},
                 "picture.persons.address.country": {'type': 'text'},

                 "picture.museum": {'type': 'object'},
                 "picture.museum.name": {'type': 'text'},
                 "picture.museum.address": {'type': 'object'},
                 "picture.museum.address.country": {'type': 'text'},
                 "picture.museum.address.street": {'type': 'text'}, "picture.museum.persona": {'type': 'object'},
                 "picture.museum.persona.name": {'type': 'text'},
                 "picture.museum.persona.address": {'type': 'object'},
                 "picture.museum.persona.address.country": {'type': 'text'},
                 "picture.museum.persona.address.city": {'type': 'text'},
             },
             }
        ]
