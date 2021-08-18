# -*- coding: utf-8 -*-
import codecs
import json
import os

from django.conf import settings
from django.db import migrations
from iam.contrib.iam_migration.migrator import IAMMigrator


def forward_func(apps, schema_editor):

    migrator = IAMMigrator(Migration.migration_json)
    migrator.migrate()


class Migration(migrations.Migration):
    migration_json = "0003_cluster.json"

    dependencies = [('bcs_iam_migration', '0002_bk_bcs_app_202108181450')]

    operations = [migrations.RunPython(forward_func)]
