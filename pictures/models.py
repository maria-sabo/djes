from django.db import models
from django.db.models import Model

from es_model.esmodel import EsModel, EsTextField


class Author(EsModel):
    name = models.TextField()
    date_birth = models.DateField()
    date_death = models.DateField()
    country_birth = models.TextField()
    note = models.CharField(default='', max_length=10000)

    class Meta:
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
            }
        ]


class Address(EsModel):
    country = EsTextField()
    city = EsTextField()
    street = EsTextField()
    house = EsTextField()


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
                 "picture.museum": {'type': 'object'},
                 "picture.museum.name": {'type': 'text'},
                 "picture.museum.address": {'type': 'object'},
                 "picture.museum.address.country": {'type': 'text'},
                 "picture.museum.persona": {'type': 'object'},
                 "picture.museum.persona.name": {'type': 'text'},
                 "picture.museum.persona.address": {'type': 'object'},
                 "picture.museum.persona.address.country": {'type': 'text'},
                 "picture.persons": {'type': 'nested'},
                 "picture.persons.name": {'type': 'text'},
                 "picture.persons.address": {'type': 'object'},
                 "picture.persons.address.country": {'type': 'text'},
             },
             }
        ]
