# -*- coding: utf-8 -*-
from rest_framework import serializers


class FetchLogsSLZ(serializers.Serializer):
    container_name = serializers.CharField()
    tail_lines = serializers.IntegerField(default=30)
    since_time = serializers.CharField(default="")
    span = serializers.IntegerField(default=0)
    previous = serializers.BooleanField(default=False)


class DownloadLogsSLZ(serializers.Serializer):
    container_name = serializers.CharField()
    previous = serializers.BooleanField(default=False)
