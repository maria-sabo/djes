import json

from django.shortcuts import get_object_or_404, render
from elasticsearch import Elasticsearch

from pictures.models import Picture, Author, Museum


def index(request):
    latest_pictures_list = Picture.objects.all()
    return render(request, 'index.html', {'latest_pictures_list': latest_pictures_list})


def pictures(request):
    latest_pictures_list = Picture.objects.all()
    return render(request, 'pictures.html', {'latest_pictures_list': latest_pictures_list})


def authors(request):
    latest_authors_list = Author.objects.all()
    return render(request, 'authors.html', {'latest_authors_list': latest_authors_list})


def museums(request):
    latest_museums_list = Museum.objects.all()
    return render(request, 'museums.html', {'latest_museums_list': latest_museums_list})


def p_detail(request, picture_id):
    picture = get_object_or_404(Picture, pk=picture_id)
    return render(request, 'p_detail.html', {'picture': picture})


def a_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, 'a_detail.html', {'author': author})


def m_detail(request, museum_id):
    museum = get_object_or_404(Museum, pk=museum_id)
    return render(request, 'm_detail.html', {'museum': museum})


def create_index(request):
    hosts = ['localhost']
    es = Elasticsearch(hosts)
    index_name = 'i_pictures'

    # ask
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name)
    latest_pictures_list = Picture.objects.all()
    i = 1
    for obj in latest_pictures_list:
        json_obj = json.dumps(obj.repr_json(), cls=ComplexEncoder)
        res = es.index(index=index_name, doc_type='t_pictures', body=json_obj, id=i)
        i = i + 1
        # print(json_obj, '\n', res)
        print(res)
    latest_list = es.search(index='i_pictures')
    latest_list = latest_list['hits']['hits']
    return render(request, 'create_index.html', {'latest_list': latest_list})


def create_filter_for_pic(request):
    latest_list = Picture.objects.all()

    received_text = request.GET.get('search_text')
    print(received_text)
    for pic in latest_list:
        latest_list = latest_list.filter(name__contains=received_text)
    return render(request, 'create_filter_for_pic.html', {'latest_list': latest_list})


def create_index_for_pic(request):
    received_text = request.GET.get('search_text')
    hosts = ['localhost']
    es = Elasticsearch(hosts)

    my_query = {'query': {'match_phrase': {'name': str(received_text)}}}
    latest_list = es.search(body=my_query, index='i_pictures')

    print(my_query)
    print(latest_list)

    print(latest_list['hits']['total']['value'])
    print(latest_list['_shards']['successful'])
    res = []
    for hit in latest_list['hits']['hits']:
        res.append(hit["_source"])
        print(hit["_source"])
    data = [doc for doc in latest_list['hits']['hits']]
    for doc in data:
        print(" %s" % (doc['_source']['name']))
    return render(request, 'create_index_for_pic.html', {'res': res})


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)
