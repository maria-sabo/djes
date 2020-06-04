from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from elasticsearch import Elasticsearch

from es_model.esmodel import EsModel
from esf_model.esfmodel import EsfModel
from pictures.models import Picture, Author, Museum, TestModel


def index(request):
    pictures_list = Picture.objects.all()
    return render(request, 'index.html', {'pictures_list': pictures_list})


def pictures(request):
    pictures_list = Picture.objects.all()
    return render(request, 'pictures.html', {'pictures_list': pictures_list})


def authors(request):
    authors_list = Author.objects.all()
    return render(request, 'authors.html', {'authors_list': authors_list})


def museums(request):
    museums_list = Museum.objects.all()
    return render(request, 'museums.html', {'museums_list': museums_list})


def p_detail(request, picture_id):
    picture = get_object_or_404(Picture, pk=picture_id)
    return render(request, 'p_detail.html', {'picture': picture})


def a_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, 'a_detail.html', {'author': author})


def m_detail(request, museum_id):
    museum = get_object_or_404(Museum, pk=museum_id)
    return render(request, 'm_detail.html', {'museum': museum})


def create_index_flag_mapping(request):
    res = EsModel.create_indices(True)
    messages.info(request, str(res))
    return redirect('/pictures/')


def create_index_flag(request):
    res = EsModel.create_indices(False)
    messages.info(request, str(res))
    return redirect('/pictures/')


def create_index_flag_mapping_f(request):
    res = EsfModel.create_indices(True)
    messages.info(request, str(res))

    return redirect('/pictures/')


def create_index_flag_f(request):
    res = EsfModel.create_indices(False)
    messages.info(request, str(res))
    return redirect('/pictures/')


def delete_index(request):
    es = Elasticsearch(['localhost'])
    res = es.indices.delete('_all')
    messages.info(request, res)
    return redirect('/pictures/')


def show_index(request):
    es = Elasticsearch(['localhost'])
    res = es.search()
    messages.info(request, res)
    return redirect('/pictures/')


def show_mapping(request):
    es = Elasticsearch(['localhost'])
    res = es.indices.get_mapping()
    messages.info(request, res)
    return redirect('/pictures/')


def show_log(request):
    # f = open('log-file.log')
    # for line in f:
    #     res.append(line)
    #     res.append('\n')
    with open('log-file.log', 'r') as f:
        res = [x.strip() for x in f.readlines()]
    messages.info(request, res)
    return redirect('/pictures/')


def alien_index1(request):
    res = []
    messages.info(request, res)
    return redirect('/pictures/')


def create_filter_for_pic(request):
    res = Picture.objects.all()
    received_text = request.GET.get('search_text')
    print(received_text)
    res = res.filter(name__contains=received_text)
    return render(request, 'search.html', {'res': res})


def create_es_for_pic(request):
    received_text = request.GET.get('search_text')
    es = Elasticsearch(['localhost'])

    my_query = {'query': {'multi_match': {'query': str(received_text)}}}
    latest_list = es.search(body=my_query, index='i_picture')

    pres = []
    for hit in latest_list['hits']['hits']:
        pres.append(int(hit["_id"]))
        print(int(hit["_id"]))

    res = Picture.objects.filter(id__in=pres)
    data = [doc for doc in latest_list['hits']['hits']]
    for doc in data:
        print(" %s" % (doc['_source']['name']))
    return render(request, 'search.html', {'res': res})
