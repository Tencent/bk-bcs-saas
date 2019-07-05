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
import time
import json

from django.db import models

from .base import BaseModel, logger
from .mixins import ResourceMixin, ConfigMapAndSecretMixin, PodMixin


class K8sResource(BaseModel):
    config = models.TextField("配置信息")
    name = models.CharField("名称", max_length=255, default='')

    class Meta:
        abstract = True
        ordering = ('created',)

    def save(self, *args, **kwargs):
        # TODO mark refactor 这段代码为了保证兼容性，后面只保留一种条件
        if isinstance(self.config, dict):
            self.name = self.config.get('metadata', {}).get('name')
            self.config = json.dumps(self.config)
        else:
            config = json.loads(self.config)
            self.name = config.get('metadata', {}).get('name')
        super().save(*args, **kwargs)

    @classmethod
    def perform_create(cls, **kwargs):
        return cls.objects.create(**kwargs)

    @classmethod
    def perform_update(cls, old_id, **kwargs):
        return cls.objects.create(**kwargs)

    def get_config(self):
        try:
            config = json.loads(self.config)
        except Exception as e:
            logger.exception(f"解析 {self.__class__.__name__}({self.id}) config 异常")
            return {}
        return config

    def get_res_config(self, is_simple):
        c = {'id': self.id, 'name': self.name}
        if not is_simple:
            c['config'] = self.get_config()
        return c

    # TODO refactor 保留get_name仅仅为了兼容，因为太多模块这么用了，后面去掉
    @property
    def get_name(self):
        config = self.get_config()
        if not config:
            return None
        return config.get('metadata', {}).get('name')


class K8sPodResource(K8sResource):
    deploy_tag = models.CharField(max_length=32, default='',
                                  help_text="每次保存时会生成新的应用记录，用deploy_tag来记录与其他资源的关联关系")
    desc = models.TextField("描述", help_text="前台展示字段，bcs api 中无该信息")

    class Meta:
        abstract = True

    @classmethod
    def perform_create(cls, **kwargs):
        kwargs['deploy_tag'] = int(time.time() * 1000000)
        return super().perform_create(**kwargs)

    @classmethod
    def perform_update(cls, old_id, **kwargs):
        try:
            resource = cls.objects.get(id=old_id)
        except cls.DoesNotExist:
            raise cls.DoesNotExist(f"{cls.__name__} Id ({old_id}) 不存在")
        # 需要与保留其他资源的关联关系，所以更新后的记录 service_tag 要与原来的记录保持一致
        deploy_tag = resource.deploy_tag
        if not deploy_tag:
            deploy_tag = int(time.time() * 1000000)
        kwargs['deploy_tag'] = deploy_tag
        return super().perform_update(old_id, **kwargs)

    def get_res_config(self, is_simple):
        c = super().get_res_config(is_simple)
        if not is_simple:
            c.update({
                'deploy_tag': self.deploy_tag,
                'desc': self.desc,
            })
        return c

    def get_labels(self):
        config = self.get_config()
        return config.get('spec', {}).get(
            'template', {}).get('metadata', {}).get('labels', {})

    def get_ports(self):
        ports = []
        for container in self.get_containers():
            for port in container.get('ports'):
                ports.append({
                    'name': port.get('name'),
                    'containerPort': port.get('containerPort'),
                    'id': port.get('id')
                })
        return ports


class K8sConfigMap(K8sResource, ConfigMapAndSecretMixin):
    pass


class K8sSecret(K8sResource, ConfigMapAndSecretMixin):
    pass


class K8sDeployment(K8sPodResource, PodMixin):
    @classmethod
    def get_resources_info(cls, resource_id_list):
        resource_data = []
        robj_qsets = cls.objects.filter(id__in=resource_id_list)
        for robj in robj_qsets:
            resource_data.append({
                'deploy_tag': robj.deploy_tag,
                'deploy_name': robj.name
            })
        return resource_data


class K8sDaemonSet(K8sPodResource, PodMixin):
    pass


class K8sJob(K8sPodResource, PodMixin):
    pass


class K8sStatefulSet(K8sPodResource, PodMixin):
    service_tag = models.CharField(u"关联的K8sService 标识", max_length=32)

    def get_res_config(self, is_simple):
        c = super().get_res_config(is_simple)
        if not is_simple:
            c['service_tag'] = self.service_tag
        return c


class K8sService(K8sResource, ResourceMixin):
    """
    service 中的 ports 一定是在 k8s Deployment 中有的。Deployment(ports) 大于等于 service(ports)
    """
    deploy_tag_list = models.TextField("关联的Deployment ID", help_text="可以关联多个Pod,json格式存储，选填")
    service_tag = models.CharField("K8sService 标识", max_length=32,
                                   help_text="每次保存时会生成新的应用记录，用来记录与其他资源的关联关系")

    def save(self, *args, **kwargs):
        if isinstance(self.deploy_tag_list, list):
            self.deploy_tag_list = json.dumps(self.deploy_tag_list)
        return super().save()

    @classmethod
    def perform_create(cls, **kwargs):
        # TODO refactor use uuid instead of timestamp
        kwargs['service_tag'] = int(time.time() * 1000000)
        return super().perform_create(**kwargs)

    @classmethod
    def perform_update(cls, old_id, **kwargs):
        try:
            resource = cls.objects.get(id=old_id)
        except cls.DoesNotExist:
            raise cls.DoesNotExist(f"{cls.__name__} Id ({old_id}) 不存在")

        kwargs['service_tag'] = resource.service_tag
        return super().perform_update(old_id, **kwargs)

    @classmethod
    def get_resources_info(cls, resource_id_list):
        svc_list = []
        svc_qsets = cls.objects.filter(id__in=resource_id_list)
        for svc in svc_qsets:
            svc_list.append({
                'service_tag': svc.service_tag,
                'service_name': svc.name
            })
        return svc_list

    def get_res_config(self, is_simple):
        c = super().get_res_config(is_simple)
        if not is_simple:
            c.update({
                'deploy_tag_list': self.get_deploy_tag_list(),
                'service_tag': self.service_tag,
            })
        return c

    def get_ports_config(self):
        config = self.get_config()
        if not config:
            return []
        return config.get('spec', {}).get('ports', [])

    def get_deploy_tag_list(self):
        if not self.deploy_tag_list:
            return []
        deploy_tag = json.loads(self.deploy_tag_list)
        return deploy_tag

    def get_selector_labels(self):
        config = self.get_config()
        if not config:
            return {}
        return config.get('spec', {}).get('selector')

    def is_headless_service(self):
        """spec.clusterIP 为 "None"
        """
        config = self.get_config() or {}
        cluster_ip = config.get('spec', {}).get('clusterIP', '')
        if cluster_ip == 'None':
            return True
        return False


class K8sIngress(K8sResource, ResourceMixin):
    desc = models.TextField("描述", help_text="前台展示字段，bcs api 中无该信息")
    category = models.CharField("类型", max_length=16, blank=True, null=True, help_text="该字段已经废弃")


# TODO refactor

# 资源类型在前端展示的名称
# backend.apps.configuration.utils.get_real_category 方法依赖下面约定的规则
CATE_SHOW_NAME = {
    # meos:后台类型全小写，前台展示首字母大写（规则不可变）
    "application": "Application",
    "deployment": "Deployment",
    "service": "Service",
    "configmap": "ConfigMap",
    "secret": "Secret",
    # k8s:前台展示去掉 'K8s' 字符 （规则不可变）
    "K8sDeployment": "Deployment",
    "K8sService": "Service",
    "K8sConfigMap": "ConfigMap",
    "K8sSecret": "Secret",
    "K8sDaemonSet": "DaemonSet",
    "K8sJob": "Job",
    "K8sStatefulSet": "StatefulSet",
    "K8sIngress": "Ingress"
}

# 资源类型在前端展示的缩写名称
CATE_ABBR_NAME = {
    "application": "app",
    "deployment": "dep",
    "service": "svc",
    "configmap": "cm",
    "secret": "srt",
    # k8s 相关资源
    "K8sDeployment": "dep",
    "K8sService": "svc",
    "K8sConfigMap": "cm",
    "K8sSecret": "srt",
    "K8sDaemonSet": "ds",
    "K8sJob": "job",
    "K8sStatefulSet": "sts",
    "K8sIngress": "Ing"
}
