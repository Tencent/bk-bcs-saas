# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List

from django.utils import timezone

from backend.apps.configuration.models import ShowVersion

from ..models import AppRelease, ResourceManifest


@dataclass
class AppReleaseData:
    name: str
    cluster_id: str
    namespace: str
    show_version: ShowVersion
    manifest_list: List[ResourceManifest]


def gen_time_revision() -> str:
    return timezone.localtime().strftime('%Y%m%d%H%M%S')


class ReleaseManager:
    def __init__(self, release_data: AppReleaseData):
        self.release_data = release_data

    def create_release(self):
        release_data = self.release_data

        show_version = release_data.show_version
        app_release = AppRelease.objects.create(
            name=release_data.name,
            cluster_id=release_data.cluster_id,
            namespace=release_data.namespace,
            template_id=show_version.template_id,
            rel_revision=gen_time_revision(),
        )

        app_release.deploy(show_version.name, show_version.latest_revision, release_data.manifest_list)

    def update_release(self):
        app_release = AppRelease.objects.get(
            name=self.release_data.name, cluster_id=self.release_data.cluster_id, namespace=self.release_data.namespace
        )
        app_release.update()

    def delete_release(self):
        pass
