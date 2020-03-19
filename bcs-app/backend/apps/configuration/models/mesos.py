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
from django.utils.translation import ugettext_lazy as _

from .mixins import MConfigMapAndSecretMixin, PodMixin, ResourceMixin
from .base import BaseModel, logger
from backend.utils.basic import getitems


class MesosResource(BaseModel):
    config = models.TextField(u"配置信息")
    name = models.CharField(u"名称", max_length=255, default='')

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
        except Exception:
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


class ConfigMap(MesosResource, MConfigMapAndSecretMixin):
    """
    Application ->挂在卷/环境变量 ->ConfigMap
    """
    pass


class Secret(MesosResource, MConfigMapAndSecretMixin):
    """
    Application ->挂在卷/环境变量 ->Secret
    """
    pass


class HPA(MesosResource, MConfigMapAndSecretMixin):
    """HPA数据表
    """
    pass


class Application(MesosResource, PodMixin):
    """
    """
    desc = models.TextField("描述", help_text="前台展示字段，bcs api 中无该信息")
    config = models.TextField(
        "配置信息", help_text="包含：实例数量\ restart策略\kill策略\备注\调度约束\网络\容器信息")
    app_id = models.CharField("应用ID", max_length=32,
                              help_text="每次保存时会生成新的应用记录，用app_id来记录与其他资源的关联关系")

    @classmethod
    def perform_create(cls, **kwargs):
        kwargs['app_id'] = int(time.time() * 1000000)
        return super().perform_create(**kwargs)

    @classmethod
    def perform_update(cls, old_id, **kwargs):
        try:
            old_app = cls.objects.get(id=old_id)
        except cls.DoesNotExist:
            raise cls.DoesNotExist(_("{} Id ({}) 不存在").format(cls.__name__, old_id))
        # 需要与保留其他资源的关联关系，所以更新后的记录 app_id 要与原来的记录保持一致
        kwargs['app_id'] = old_app.app_id
        return super().perform_update(old_id, **kwargs)

    def _get_container_volume_users(self, volumes):
        if not volumes:
            return {}

        c_volume_users = {}
        for v in volumes:
            vol = v['volume']
            if v['type'] == 'configmap':
                c_volume_users[f"{v['type']}:{v['name']}:{vol['hostPath']}:{vol['mountPath']}"] = 'root'
            elif v['type'] == 'secret':
                c_volume_users[f"{v['type']}:{v['name']}:{vol['hostPath']}:{vol['mountPath']}"] = 'user00'

        return c_volume_users

    def _set_default_volume_users(self, config):
        volume_users = {}
        containers = getitems(config, ['spec', 'template', 'spec', 'containers'], default=[])
        for container in containers:
            volumes = container.get('volumes', [])
            volume_users[container['name']] = self._get_container_volume_users(volumes)

        config['webCache']['volumeUsers'] = volume_users

    def get_res_config(self, is_simple):
        c = super().get_res_config(is_simple)

        if not is_simple:
            # 兼容处理configmap和secret挂载卷时，指定账户
            if 'volumeUsers' not in c['config']['webCache']:
                self._set_default_volume_users(c['config'])

            c.update({
                'desc': self.desc,
                'app_id': self.app_id
            })
        return c

    def get_instance(self):
        config = self.get_config()
        if not config:
            return None
        return config.get('spec', {}).get('instance')

    def _get_related_resource(self, container, resource_name):
        resource_list = []
        for env in container.get('env_list'):
            if env.get('type') == resource_name:
                env_name = env.get('value').split('.')[0]
                resource_list.append(env_name)

        for vol in container.get('volumes'):
            if vol.get('type') == resource_name:
                resource_list.append(vol.get('name'))

        return list(set(resource_list))

    def get_related_resource(self, instance_entity):
        """获取 Application 依赖的资源
        """
        # Application 依赖的资源在挂载卷/环境变量 的 configmap & secret 中
        configmap_name_list = []
        secret_name_list = []
        for container in self.get_containers():
            configmap_name_list.extend(self._get_related_resource(container, 'configmap'))
            secret_name_list.extend(self._get_related_resource(container, 'secret'))
        return list(set(configmap_name_list)), list(set(secret_name_list))

    @classmethod
    def get_resources_info(cls, resource_id_list):
        resource_data = []
        robj_qsets = cls.objects.filter(id__in=resource_id_list)
        for robj in robj_qsets:
            resource_data.append({
                'app_id': robj.app_id,
                'app_name': robj.name
            })
        return resource_data


class Deplpyment(MesosResource, ResourceMixin):
    """
    Deplpyment 是基于 Application 构建的
    本表只存储 Deplpyment 本身特性的相关策略

    {
        "app_id": "",
        "desc": "this is a desc",
        "config": {
            "strategy": {
                "type": "RollingUpdate",
                "rollingupdate": {
                    "maxUnavilable": 1,
                    "maxSurge": 1,
                    "upgradeDuration": 60,
                    "autoUpgrade": false,
                    "rollingOrder": "CreateFirst"
                }
            },
            "pause": false,
        }
    }
    """
    name = models.CharField("名称", max_length=255)
    app_id = models.CharField("关联的Application ID", max_length=32)
    desc = models.TextField("描述", help_text="前台展示字段，bcs api 中无该信息")
    config = models.TextField("配置信息", help_text="包含：升级策略")

    def save(self, *args, **kwargs):
        if isinstance(self.config, dict):
            self.config = json.dumps(self.config)

        super(MesosResource, self).save(*args, **kwargs)

    def get_res_config(self, is_simple):
        c = super().get_res_config(is_simple)
        if not is_simple:
            c.update({
                'app_id': self.app_id,
                'desc': self.desc
            })
        return c

    # TODO refactor 保留get_name仅仅为了兼容，因为太多模块这么用了，后面去掉
    @property
    def get_name(self):
        return self.name

    @classmethod
    def get_resources_info(cls, resource_id_list):
        resource_data = []
        robj_qsets = cls.objects.filter(id__in=resource_id_list)
        for robj in robj_qsets:
            resource_data.append({
                'deployment_name': robj.name
            })
        return resource_data


class Service(MesosResource, ResourceMixin):
    """
    service 中的 ports 一定是在 application 中有的。application(ports) 大于等于 service(ports)
    """
    app_id = models.TextField("关联的Application ID", help_text="可以关联多个Application")

    def save(self, *args, **kwargs):
        # 保存时,name字段单独保存
        if isinstance(self.config, dict):
            self.name = self.config.get('metadata', {}).get('name')
            self.config = json.dumps(self.config)
        else:
            config = json.loads(self.config)
            self.name = config.get('metadata', {}).get('name')

        # 保存关联应用的权重信息
        try:
            app_id_value = json.loads(self.app_id)
        except Exception:
            app_id_value = self.app_id
            self.app_id = json.dumps(self.app_id)

        if isinstance(app_id_value, dict):
            return super(MesosResource, self).save(*args, **kwargs)

        if not isinstance(app_id_value, list):
            app_id_list = app_id_value.split(',') if self.app_id else []
        else:
            app_id_list = app_id_value

        if not app_id_list:
            self.app_id = json.dumps({})
            return super(MesosResource, self).save(*args, **kwargs)

        app_id = {}
        # 计算每个应用的权重
        app_len = len(app_id_list)
        arg_weight = 100 // app_len
        other_weight = 100 % app_len
        app_id[app_id_list[0]] = arg_weight + other_weight
        for _app_id in app_id_list[1:]:
            app_id[_app_id] = arg_weight
        self.app_id = json.dumps(app_id)

        super(MesosResource, self).save(*args, **kwargs)

    def get_res_config(self, is_simple):
        c = super().get_res_config(is_simple)
        if not is_simple:
            c.update({
                'app_id': self.get_app_id_list(),
                'app_weight': self.get_app_weight(),
            })
        return c

    def get_ports_config(self):
        config = self.get_config()
        if not config:
            return []
        return config.get('spec', {}).get('ports', [])

    def get_app_id_list(self):
        app_id = json.loads(self.app_id)
        return app_id.keys()

    def get_app_weight(self):
        app_id = json.loads(self.app_id)
        return app_id

    def is_related_lb(self):
        config = self.get_config()
        if not config:
            return False
        return config.get('isLinkLoadBalance')

    @classmethod
    def get_resources_info(cls, resource_id_list):
        svc_list = []
        svc_qsets = cls.objects.filter(id__in=resource_id_list)
        for svc in svc_qsets:
            svc_info = {
                'name': svc.name,
                'port': svc.get_ports_config()
            }
            svc_list.append(svc_info)
        return svc_list


class Ingress(MesosResource, MConfigMapAndSecretMixin):
    """mesos ingress表
    """
    pass
