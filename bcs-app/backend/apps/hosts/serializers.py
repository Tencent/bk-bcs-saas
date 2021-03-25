# -*- coding: utf-8 -*-
from typing import Dict

from rest_framework import serializers

from backend.apps.cluster.constants import ClusterNetworkType

from .models import HostApplyTaskLog


class ApplyHostDataSLZ(serializers.Serializer):
    region = serializers.CharField()
    network_type = serializers.ChoiceField(
        choices=ClusterNetworkType.get_choices(),
        default=ClusterNetworkType.OVERLAY.value,
    )
    cvm_type = serializers.CharField()
    disk_size = serializers.IntegerField()
    replicas = serializers.IntegerField()

    def validate(self, data: Dict) -> Dict:
        data.update(self.context)
        return data


class TaskLogSLZ(serializers.ModelSerializer):
    class Meta:
        model = HostApplyTaskLog
        fields = ("created", "task_url", "operator", "status", "is_finished", "task_logs")


try:
    from .serializers_ext import GetCVMTypeDataSLZ
except ImportError:
    pass
