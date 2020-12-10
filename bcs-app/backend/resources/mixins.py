# -*- coding: utf-8 -*-
from kubernetes import client


class APIExtensionsAPIClassMixins:
    """
    支持资源类型: Ingress
    """

    def get_api_cls_list(self, api_client):
        resp = client.ApiextensionsApi(api_client).get_api_group()
        # 假定preferred_version.group_version在第一个
        group_versions = [v.group_version for v in resp.versions]

        api_cls_list = []
        for group_version in group_versions:
            group, version = group_version.split("/")
            api_cls_list.append(f"{group.split('.')[0].capitalize()}{version.capitalize()}Api")
        return api_cls_list


class CustomObjectsAPIClassMixins:
    def get_api_cls_list(self, api_client):
        return ["CustomObjectsApi"]


class CoreAPIClassMixins:
    """
    支持资源类型: ConfigMap/Endpoints/Event/Namespace/Node/Pod/PersistentVolume/secret等
    """
    def get_api_cls_list(self, api_client):
        versions = client.CoreApi(api_client).get_api_versions()
        return [f"Core{ver.capitalize()}Api" for ver in versions]
