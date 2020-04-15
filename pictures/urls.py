from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pictures/$', views.pictures, name='pictures'),
    url(r'^authors/$', views.authors, name='authors'),
    url(r'^museums/$', views.museums, name='museums'),
    url(r'^create_index/$', views.create_index, name='create_index'),
    url(r'^pictures/create_filter_for_pic/$', views.create_filter_for_pic, name='create_filter_for_pic'),
    url(r'^pictures/create_index_for_pic/$', views.create_index_for_pic, name='create_index_for_pic'),
    # ex: /tables/5/
    url(r'^pictures/(?P<picture_id>[0-9]+)/$', views.p_detail, name='p_detail'),
    url(r'^authors/(?P<author_id>[0-9]+)/$', views.a_detail, name='a_detail'),
    url(r'^museums/(?P<museum_id>[0-9]+)/$', views.m_detail, name='m_detail'),
]
