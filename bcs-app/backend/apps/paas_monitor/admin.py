# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
# Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
from django.contrib import admin
from django import forms

from . import models


class MetricSourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'kind', 'category', 'dimension', 'metric_type', 'data_src',
                    'conversion_unit', 'aggregators', 'intervals')
    search_fields = ('name', 'kind', 'category', 'dimension', 'metric_type', 'data_src',
                     'conversion_unit', 'aggregators', 'intervals')


class AlarmConfigAdmin(admin.ModelAdmin):
    list_filter = ('status', )
    list_display = ('id', 'project_id', 'name', 'status', 'category', 'dimension', 'metric_source_id', 'strategy_id')
    search_fields = ('project_id', 'name', 'status', 'category', 'dimension', 'metric_source_id', 'strategy_id')


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_id', 'name', 'users')
    search_fields = ('project_id', 'name')


class EventConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_id', 'name', 'service_name', 'event_type', 'creator', 'is_enabled', 'updated')
    search_fields = ('project_id', 'name')


class LogGroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_id', 'name')
    search_fields = ('project_id', 'name')


class LogStreamForm(forms.ModelForm):

    log_group_id = forms.ModelChoiceField(queryset=models.LogGroups.objects.all())

    class Meta:
        model = models.LogStream
        fields = '__all__'

    def clean_log_group_id(self):
        return self.cleaned_data['log_group_id'].id


class LogStreamAdmin(admin.ModelAdmin):
    form = LogStreamForm
    list_display = ('id', 'log_group_id', 'project_id', 'name', 'type')
    search_fields = ('project_id', 'name')


class LogMonitorForm(forms.ModelForm):

    log_stream_id = forms.ModelChoiceField(queryset=models.LogStream.objects.all())

    class Meta:
        model = models.LogMonitor
        fields = '__all__'

    def clean_log_stream_id(self):
        return self.cleaned_data['log_stream_id'].id


class LogMonitorAdmin(admin.ModelAdmin):
    form = LogMonitorForm
    list_display = ('id', 'log_stream_id', 'project_id', 'name', 'monitor_item_config_id')
    search_fields = ('project_id', 'name')


class MonitorItemConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_id', 'name', 'is_enabled', 'src_type', 'scenario')
    search_fields = ('project_id', 'name')


class AlarmShieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_id', 'shield_type', 'shield_start_time', 'shield_end_time', 'is_enabled')


class JaAlarmAlarminstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'alarm_source_id', 'status', 'alarm_type', 'user_status')
    search_fields = ('alarm_source_id', 'status', 'alarm_type', 'user_status')


admin.site.register(models.MetricSource, MetricSourceAdmin)
admin.site.register(models.AlarmConfig, AlarmConfigAdmin)
admin.site.register(models.UserGroup, UserGroupAdmin)
admin.site.register(models.EventConfig, EventConfigAdmin)
admin.site.register(models.LogGroups, LogGroupsAdmin)
admin.site.register(models.LogStream, LogStreamAdmin)
admin.site.register(models.LogMonitor, LogMonitorAdmin)
admin.site.register(models.MonitorItemConfig, MonitorItemConfigAdmin)
admin.site.register(models.AlarmShield, AlarmShieldAdmin)
admin.site.register(models.JaAlarmAlarminstance, JaAlarmAlarminstanceAdmin)
