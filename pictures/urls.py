from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pictures/$', views.pictures, name='pictures'),
    url(r'^authors/$', views.authors, name='authors'),
    url(r'^museums/$', views.museums, name='museums'),

    url(r'^mapping_pic/$', views.mapping_pic, name='mapping_pic'),
    url(r'^mapping/change_mapp_pic/$', views.change_mapp_pic, name='change_mapp_pic'),
    url(r'^mapping_auth/$', views.mapping_auth, name='mapping_auth'),
    url(r'^mapping/change_mapp_auth/$', views.change_mapp_auth, name='change_mapp_auth'),
    url(r'^mapping_mus/$', views.mapping_mus, name='mapping_mus'),
    url(r'^mapping/change_mapp_mus/$', views.change_mapp_mus, name='change_mapp_mus'),

    url(r'^show_index/$', views.show_index, name='show_index'),
    url(r'^show_mapping/$', views.show_mapping, name='show_mapping'),
    url(r'^delete_index/$', views.delete_index, name='delete_index'),
    url(r'^show_log/$', views.show_log, name='show_log'),
    url(r'^pictures/pictures_search/$', views.pictures_search, name='pictures_search'),
    # url(r'^pictures/create_filter_for_pic/$', views.create_filter_for_pic, name='create_filter_for_pic'),

    url(r'^create_index_flag/$', views.create_index_flag, name='create_index_flag'),
    url(r'^create_index_flag_f/$', views.create_index_flag_f, name='create_index_flag_f'),
    url(r'^create_index_flag_mapping/$', views.create_index_flag_mapping, name='create_index_flag_mapping'),
    url(r'^create_index_flag_mapping_f/$', views.create_index_flag_mapping_f, name='create_index_flag_mapping_f'),

    url(r'^alien_index1/$', views.alien_index1, name='alien_index1'),
    # ex: /tables/5/
    url(r'^pictures/(?P<picture_id>[0-9]+)/$', views.p_detail, name='p_detail'),
    url(r'^authors/(?P<author_id>[0-9]+)/$', views.a_detail, name='a_detail'),
    url(r'^museums/(?P<museum_id>[0-9]+)/$', views.m_detail, name='m_detail'),
]
