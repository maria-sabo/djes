from elasticsearch import Elasticsearch


def es_client(hosts):
    return Elasticsearch(hosts)