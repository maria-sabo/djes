import time
from django.test import TestCase
from elasticsearch import Elasticsearch
from pictures.models import Address, Person, Address2, Person2


class EsModelTestCase(TestCase):
    es = Elasticsearch(['localhost'])

    test_address = Address.objects.create(country='Russia', city='Moscow', street='Tverskaya street',
                                          house='house 5')
    test_person = Person.objects.create(name="Test Person", address=test_address)

    test_person._meta.mappings = [
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
        {
            "es_index_name": "iii_person",
            "es_doc_type": "ttt_person",
            "es_mapping": {
            },
        },
    ]

    def test_EsModel_ob2es(self):
        # проверка работы метода obj2es - экземпляр модели в соответствии с заданным мэппингом переводится в JSON
        self.test_person._meta.es_mapping = self.test_person._meta.mappings[0].get("es_mapping")
        o1 = self.test_person.obj2es()
        self.test_person._meta.es_mapping = self.test_person._meta.mappings[1].get("es_mapping")
        o2 = self.test_person.obj2es()
        self.test_person._meta.es_mapping = self.test_person._meta.mappings[2].get("es_mapping")
        o3 = self.test_person.obj2es()

        self.assertEqual(o1,
                         '{"name": "Test Person", "address": {"country": "Russia", "city": "Moscow", "street": '
                         '"Tverskaya street", "house": "house 5"}}')
        self.assertEqual(o2, '{"name": "Test Person"}')
        self.assertEqual(o3, '{}')

    def test_EsModel_mod2es(self):
        # проверка работы метода mod2es - создает словарь маппинга в соответствии с
        # переданными в "es_mapping" значениями
        self.test_person._meta.es_mapping = self.test_person._meta.mappings[0].get("es_mapping")
        Person._meta.es_mapping = Person._meta.mappings[0].get("es_mapping")
        m1 = Person.mod2es(Person)
        Person._meta.es_mapping = Person._meta.mappings[1].get("es_mapping")
        m2 = Person.mod2es(Person)
        Person._meta.es_mapping = Person._meta.mappings[2].get("es_mapping")
        m3 = Person.mod2es(Person)

        self.assertEqual(m1,
                         '{"name": {"type": "text"}, '
                         '"address": {"type": "object", "properties": {'
                         '"country": {"type": "text"}, '
                         '"city": {"type": "text"}, '
                         '"street": {"type": "text"}, '
                         '"house": {"type": "text"}}}}')

        self.assertEqual(m2, '{"name": {"type": "text"}}')
        self.assertEqual(m3, '{}')

    def test_EsModel_create_indices_for_model_with_mapping(self):
        # проверка создания индексов на модель Person, используя маппинг
        Person.create_indices_for_model(Person, True, self.es)
        time.sleep(1)
        # передаем ES документы
        Person.put_document(self.test_person, self.es)
        time.sleep(1)
        map1 = self.es.indices.get_mapping(index='i_person')
        time.sleep(1)
        map2 = self.es.indices.get_mapping(index='ii_person')
        time.sleep(1)
        map3 = self.es.indices.get_mapping(index='iii_person')
        time.sleep(1)

        res1 = self.es.search(index='i_person')
        time.sleep(1)
        res2 = self.es.search(index='ii_person')
        time.sleep(1)
        res3 = self.es.search(index='iii_person')
        time.sleep(1)

        self.assertDictEqual(map1, {'i_person': {'mappings': {'properties': {'address': {
            'properties': {'city': {'type': 'text'}, 'country': {'type': 'text'},
                           'house': {'type': 'text'}, 'street': {'type': 'text'}}},
            'name': {'type': 'text'}}}}})
        self.assertDictEqual(map2, {'ii_person': {'mappings': {'properties': {'name': {'type': 'text'}}}}})
        self.assertDictEqual(map3, {'iii_person': {'mappings': {}}})

        self.assertDictEqual(res1['hits']['hits'][0].get("_source"),
                             {'name': 'Test Person',
                              'address': {
                                  'country': 'Russia',
                                  'city': 'Moscow',
                                  'street': 'Tverskaya street',
                                  'house': 'house 5'}})

        self.assertDictEqual(res2['hits']['hits'][0].get("_source"),
                             {'name': 'Test Person'})
        self.assertDictEqual(res3['hits']['hits'][0].get("_source"), {})

    def test_EsModel_create_indices_for_model_without_mapping(self):
        self.maxDiff = None
        # создание индексов на модель Person без учета маппинга
        Person.create_indices_for_model(Person, False, self.es)
        map1 = self.es.indices.get_mapping(index='i_person')
        time.sleep(1)
        map2 = self.es.indices.get_mapping(index='ii_person')
        time.sleep(1)
        map3 = self.es.indices.get_mapping(index='iii_person')
        time.sleep(1)

        Person.put_document(self.test_person, self.es)
        time.sleep(1)
        map4 = self.es.indices.get_mapping(index='i_person')
        time.sleep(1)
        map5 = self.es.indices.get_mapping(index='ii_person')
        time.sleep(1)
        map6 = self.es.indices.get_mapping(index='iii_person')
        time.sleep(1)

        res1 = self.es.search(index='i_person')
        time.sleep(1)
        res2 = self.es.search(index='ii_person')
        time.sleep(1)
        res3 = self.es.search(index='iii_person')
        time.sleep(1)

        self.assertDictEqual(map1, {'i_person': {'mappings': {}}})
        self.assertDictEqual(map2, {'ii_person': {'mappings': {}}})
        self.assertDictEqual(map3, {'iii_person': {'mappings': {}}})

        self.assertDictEqual(map4, {'i_person': {'mappings': {'properties': {'address': {
            'properties': {'city': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                           'country': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                           'house': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                           'street': {'type': 'text',
                                      'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}}},
            'name': {'type': 'text', 'fields': {
                'keyword': {'type': 'keyword',
                            'ignore_above': 256}}}}}}})
        self.assertDictEqual(map5, {'ii_person': {'mappings': {'properties': {
            'name': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}}}}})
        self.assertDictEqual(map6, {'iii_person': {'mappings': {}}})

        self.assertDictEqual(res1['hits']['hits'][0].get("_source"),
                             {'name': 'Test Person',
                              'address': {
                                  'country': 'Russia',
                                  'city': 'Moscow',
                                  'street': 'Tverskaya street',
                                  'house': 'house 5'}})

        self.assertDictEqual(res2['hits']['hits'][0].get("_source"),
                             {'name': 'Test Person'})
        self.assertDictEqual(res3['hits']['hits'][0].get("_source"), {})


class EsfModelTestCase(TestCase):
    es = Elasticsearch(['localhost'])
    test_address = Address2.objects.create(country='Russia', city='Moscow', street='Tverskaya street',
                                           house='house 5')
    test_person = Person2.objects.create(name="Test Person", address=test_address)

    def test_EsfModel_obj2es(self):
        # проверка работы метода obj2es - экземпляр модели в соответствии с заданным мэппингом переводится в JSON
        o1 = self.test_person.obj2es()
        self.assertEqual(o1,
                         '{"name": "Test Person", "address": '
                         '{"country": "Russia", "city": "Moscow", "street": "Tverskaya street", "house": "house 5"}}')

    def test_EsfModel_mod2es(self):
        # проверка работы метода mod2es - создает словарь маппинга в соответствии с
        # переданными в параметре поля es_map значением
        m1 = Person2.mod2es(Person2)
        self.assertEqual(m1,
                         '{"name": {"type": "text"}, "address": '
                         '{"type": "object", '
                         '"properties":{'
                         '"country": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}},'
                         '"city": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}, '
                         '"street": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}, '
                         '"house": {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}}}}')

    def test_EsfModel_create_indices_for_model_with_mapping(self):
        # проверка создания индексов на модель Person, используя маппинг
        Person2.create_indices_for_model(Person2, True, self.es)
        time.sleep(1)
        # передаем ES документы
        Person2.put_document(self.test_person, self.es)
        time.sleep(1)
        map1 = self.es.indices.get_mapping(index='i_person2')

        res1 = self.es.search(index='i_person')
        time.sleep(1)

        self.assertDictEqual(map1, {'i_person2': {'mappings': {'properties': {
            'address': {'properties':
                            {'city': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                             'country': {'type': 'text',
                                         'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                             'house': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                             'street': {'type': 'text',
                                        'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}}},
            'name': {'type': 'text'}}}}})

        self.assertDictEqual(res1['hits']['hits'][0].get("_source"),
                             {'name': 'Test Person',
                              'address': {'country': 'Russia', 'city': 'Moscow',
                                          'street': 'Tverskaya street', 'house': 'house 5'}})

    def test_EsfModel_create_indices_for_model_without_mapping(self):
        self.maxDiff = None
        # создание индексов на модель Person без учета маппинга
        Person2.create_indices_for_model(Person2, False, self.es)
        map1 = self.es.indices.get_mapping(index='i_person2')
        time.sleep(1)

        Person2.put_document(self.test_person, self.es)
        time.sleep(1)

        res1 = self.es.search(index='i_person2')
        time.sleep(1)

        self.assertDictEqual(map1, {'i_person2': {'mappings': {}}})
        self.assertDictEqual(res1['hits']['hits'][0].get("_source"),
                             {'name': 'Test Person',
                              'address': {'country': 'Russia', 'city': 'Moscow',
                                          'street': 'Tverskaya street', 'house': 'house 5'}})