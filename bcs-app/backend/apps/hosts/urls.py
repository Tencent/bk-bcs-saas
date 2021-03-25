# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^apply/$", views.ApplyHostViewSet.as_view({"post": "apply_host"})),
    url(r"^apply/logs/$", views.ApplyHostViewSet.as_view({"get": "get_task_log"})),
]


try:
    from .urls_ext import urlpatterns as urlpatterns_ext

    urlpatterns += urlpatterns_ext
except ImportError:
    pass
