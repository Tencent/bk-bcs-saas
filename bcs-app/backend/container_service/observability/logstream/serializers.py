# -*- coding: utf-8 -*-
from rest_framework import serializers


class GetLogStreamSLZ(serializers.Serializer):
    container_name = serializers.CharField()
    tail_lines = serializers.IntegerField(default=30)
    since_time = serializers.CharField(default="")
    span = serializers.IntegerField(default=0)
