import re
import json
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django_es import esmodel
from django_es.esmodel import EsModel
from django_es_f.esfmodel import EsfModel
from pictures.models import Picture, Author, Museum


def index(request):
    res = []
    return render(request, 'index.html', {'res': res})


def pictures(request):
    pictures_list = Picture.objects.all()
    return render(request, 'pictures.html', {'pictures_list': pictures_list[0:10]})


def change_mapp_pic(request):
    received_mapp = request.GET.get('mapp')
    received_mapp = json.loads(received_mapp.replace("'", '"'))
    Picture._meta.mappings = received_mapp
    print(received_mapp)
    return redirect('/pictures/')


def change_mapp_auth(request):
    received_mapp = request.GET.get('mapp')
    received_mapp = json.loads(received_mapp.replace("'", '"'))
    Author._meta.mappings = received_mapp
    print(received_mapp)
    return redirect('/pictures/')


def change_mapp_mus(request):
    received_mapp = request.GET.get('mapp')
    received_mapp = json.loads(received_mapp.replace("'", '"'))
    Museum._meta.mappings = received_mapp
    print(received_mapp)
    return redirect('/pictures/')


def mapping_pic(request):
    var = Picture._meta.mappings
    var = str(var)
    var = re.sub("^\s+|\n|\r|\t|\s+$", '', var)
    var = var.replace("},", '},\n')
    return render(request, 'mapping_pic.html', {'res': var})


def mapping_auth(request):
    var = Author._meta.mappings
    var = str(var)
    var = re.sub("^\s+|\n|\r|\t|\s+$", '', var)
    var = var.replace("},", '},\n')
    return render(request, 'mapping_auth.html', {'res': var})


def mapping_mus(request):
    var = Museum._meta.mappings
    var = str(var)
    var = re.sub("^\s+|\n|\r|\t|\s+$", '', var)
    var = var.replace("},", '},\n')
    return render(request, 'mapping_mus.html', {'res': var})


def pictures_search(request):
    received_text = request.GET.get('search_text')
    my_query = {'query': {'multi_match': {'query': str(received_text)}}}
    latest_list = esmodel.es.search(body=my_query, index='i_picture')
    pres = []
    for hit in latest_list['hits']['hits']:
        pres.append(int(hit["_id"]))
        print(int(hit["_id"]))
    res = Picture.objects.filter(id__in=pres)
    return render(request, 'search.html', {'res': res})


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
    res = EsModel.create_indices(True, True)
    messages.info(request, str(res))
    return redirect('/pictures/')


def create_index_flag(request):
    res = EsModel.create_indices(False, True)
    messages.info(request, str(res))
    return redirect('/pictures/')


def create_index_flag_mapping_f(request):
    res = EsfModel.create_indices(True, True)
    messages.info(request, str(res))
    return redirect('/pictures/')


def create_index_flag_f(request):
    res = EsfModel.create_indices(False, True)
    messages.info(request, str(res))
    return redirect('/pictures/')


def delete_index(request):
    res = esmodel.es.indices.delete('_all')
    messages.info(request, res)
    return redirect('/pictures/')


def show_index(request):
    indices_names = []
    res = []
    for elem in esmodel.es.cat.indices(format="json"):
        indices_names.append(elem['index'])
    for i in indices_names:
        ind = esmodel.es.search(index=i)
        res.append(ind["hits"]["hits"])
    messages.info(request, res)
    return redirect('/pictures/')


def show_mapping(request):
    res = esmodel.es.indices.get_mapping()
    messages.info(request, res)
    return redirect('/pictures/')


def show_log(request):
    with open('log-file.log', 'r') as f:
        res = [x.strip() for x in f.readlines()]
    messages.info(request, res)
    return redirect('/pictures/')


def alien_index1(request):
    res = []
    messages.info(request, res)
    return redirect('/pictures/')

# def create_filter_for_pic(request):
#     res = Picture.objects.all()
#     received_text = request.GET.get('search_text')
#     print(received_text)
#     res = res.filter(name__contains=received_text)
#     return res
# return render(request, 'search.html', {'res': res})
