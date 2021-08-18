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
    migration_json = "0002_project_extra.json"

    dependencies = [('bcs_iam_migration', '0001_initial')]

    operations = [migrations.RunPython(forward_func)]
