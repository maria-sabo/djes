from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect

from es_model.esmodel import EsModel
from esf_model.esfmodel import EsfModel
from pictures.for_es import es_client
from pictures.models import Picture, Author, Museum


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
    EsfModel.create_indices(True)
    res = EsfModel.put_documents()
    messages.info(request, str(res))
    return redirect('/pictures/')


def create_index_flag(request):
    EsfModel.create_indices(False)
    res = EsfModel.put_documents()
    messages.info(request, str(res))
    return redirect('/pictures/')


def delete_index(request):
    es = es_client(['localhost'])
    res = es.indices.delete('_all')
    messages.info(request, res)
    return redirect('/pictures/')


def show_index(request):
    es = es_client(['localhost'])
    latest_list = es.search()
    return render(request, 'create_index.html', {'latest_list': latest_list})


def show_mapping(request):
    es = es_client(['localhost'])
    latest_list = es.indices.get_mapping()
    return render(request, 'create_index.html', {'latest_list': latest_list})


def create_filter_for_pic(request):
    res = Picture.objects.all()
    received_text = request.GET.get('search_text')
    print(received_text)
    res = res.filter(name__contains=received_text)
    return render(request, 'search.html', {'res': res})


def create_es_for_pic(request):
    received_text = request.GET.get('search_text')
    es = es_client(['localhost'])

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
