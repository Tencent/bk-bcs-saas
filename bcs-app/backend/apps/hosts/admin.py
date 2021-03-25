# -*- coding: utf-8 -*-
from django.contrib import admin

from . import models


class HostApplyTaskLogAdmin(admin.ModelAdmin):
    list_display = ("id", "project_id", "task_id", "operator", "status", "is_finished")
    search_display = ("id", "project_id", "task_id", "operator", "status", "is_finished")


admin.site.register(models.HostApplyTaskLog, HostApplyTaskLogAdmin)
