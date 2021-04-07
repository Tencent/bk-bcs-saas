# -*- coding: utf-8 -*-
from django.conf.urls import url

from backend.apps.network.clb import views

urlpatterns = [
    url(
        r'^api/projects/(?P<project_id>\w{32})/network/clb/names/$',
        views.DescribeCLBNamesViewSet.as_view({'get': 'list'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w{32})/network/clbs/$',
        views.CLBListCreateViewSet.as_view({'get': 'list', 'post': 'create'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w{32})/network/clbs/(?P<clb_id>\d+)/$',
        views.CLBRetrieveOperateViewSet.as_view({'get': 'retrieve', 'delete': 'delete', 'put': 'update'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w{32})/network/mesos/clbs/(?P<clb_id>\d+)/$',
        views.MesosCLBOperateViewSet.as_view({'post': 'post', 'delete': 'delete'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w{32})/network/clbs/(?P<clb_id>\d+)/status/$',
        views.CLBStatusViewSet.as_view({'get': 'retrieve_status'}),
    ),
    url(
        r'^api/projects/(?P<project_id>\w{32})/network/clb/regions/$',
        views.GetCLBRegionsViewSet.as_view({'get': 'list'}),
    ),
]
