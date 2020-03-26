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
import json

from django.db import models
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from backend.apps.metric.models import Metric
from backend.apps.configuration import constants
from backend.apps.application.constants import K8S_KIND, MESOS_KIND
from backend.apps.instance.constants import LOG_CONFIG_MAP_SUFFIX, APPLICATION_ID_SEPARATOR, INGRESS_ID_SEPARATOR
from .base import BaseModel, POD_RES_LIST, logger, get_default_version, COPY_TEMPLATE
from .manager import TemplateManager, ShowVersionManager, VersionedEntityManager
from .utils import get_model_class_by_resource_name, get_secret_name_by_certid, MODULE_DICT
from . import k8s, mesos, resfile

TemplateCategory = constants.TemplateCategory
TemplateEditMode = constants.TemplateEditMode
K8sResourceName = constants.K8sResourceName
MesosResourceName = constants.MesosResourceName


def get_template_by_project_and_id(project_id, template_id):
    try:
        template = Template.objects.get(id=template_id)
    except Template.DoesNotExist:
        raise ValidationError(_("模板集(id:{})不存在").format(template_id))

    if project_id != template.project_id:
        raise ValidationError(_("模板集(id:{})不属于该项目(id:{})").format(template_id, project_id))

    return template


class Template(BaseModel):
    """
    配置模板
    """
    project_id = models.CharField("项目ID", max_length=32)
    name = models.CharField("名称", max_length=255)
    desc = models.CharField("描述", max_length=100, help_text="最多不超过50个字符")
    category = models.CharField(
        "类型", max_length=10, choices=TemplateCategory.get_choices(),
        default=TemplateCategory.CUSTOM.value)
    draft = models.TextField("草稿", default='')
    draft_time = models.DateTimeField("草稿更新时间", blank=True, null=True)
    draft_updator = models.CharField("草稿更新者", max_length=32, default='')
    draft_version = models.IntegerField("草稿对应的版本", default=0)

    edit_mode = models.CharField("编辑模式", max_length=16, choices=TemplateEditMode.get_choices(),
                                 default=TemplateEditMode.PageForm.value)

    is_locked = models.BooleanField("是否加锁", default=False)
    locker = models.CharField("加锁者", max_length=32, default='', blank=True, null=True)

    objects = TemplateManager()
    default_objects = models.Manager()

    class Meta:
        index_together = ("is_deleted", "project_id")
        unique_together = ("project_id", "name")
        ordering = ('-updated',)

    def save(self, *args, **kwargs):
        # 捕获名称重复异常
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            # TODO mark refactor use ValidationError not properly
            detail = {
                'field': [_("模板集名称{}已经存在,请重新填写").format(self.name)]
            }
            raise ValidationError(detail=detail)

    def get_draft(self):
        """获取模板集的草稿信息
        """
        if not self.draft:
            return {}
        try:
            return json.loads(self.draft)
        except Exception:
            logger.exception(f"获取模板集[id:{self.id}]的草稿出错")
            return {}

    def get_containers_from_draft(self, project_kind):
        # 只有草稿的情况
        container_list = []
        draft = self.get_draft()
        apps = []
        if project_kind == K8S_KIND:
            for resource_name in POD_RES_LIST:
                apps.extend(draft.get(resource_name) or [])
        else:
            apps = draft.get('application') or []

        for app in apps:
            config = app.get('config') or {}
            if not config:
                continue

            containers = config.get('spec', {}).get(
                'template', {}).get('spec', {}).get('containers', [])
            for con in containers:
                container_list.append({
                    'name': con.get('name'),
                    'image': con.get('image').split('/')[-1]
                })
        return container_list

    def get_containers(self, project_kind, show_version):
        """容器名称和容器镜像
        """
        # 只有草稿的情况
        if not show_version:
            return self.get_containers_from_draft(project_kind)

        try:
            ventity = VersionedEntity.objects.get(id=show_version.real_version_id)
        except VersionedEntity.DoesNotExist:
            return []

        if self.edit_mode == TemplateEditMode.PageForm.value:
            return ventity.get_containers(project_kind)
        else:
            return ventity.get_containers_from_yaml()

    @property
    def log_url(self):
        """图标，返回 None 时，前端使用默认图标
        """
        return None

    @property
    def latest_show_ver_obj(self):
        lasetest_ver = ShowVersion.objects.filter(
            template_id=self.id).order_by('-updated').first()
        return lasetest_ver

    @property
    def latest_show_version(self):
        lasetest_ver = self.latest_show_ver_obj
        if lasetest_ver:
            return lasetest_ver.name
        draft = self.get_draft
        if draft:
            return u"草稿"
        return ""

    @property
    def latest_show_version_id(self):
        lasetest_ver = self.latest_show_ver_obj
        if lasetest_ver:
            return lasetest_ver.id
        draft = self.get_draft
        if draft:
            return -1
        return -1

    @property
    def latest_version_obj(self):
        template_id = self.id
        last_version = VersionedEntity.objects.get_latest_by_template(template_id)
        if not last_version:
            return None
        return last_version

    @property
    def latest_version(self):
        template_id = self.id
        last_version = VersionedEntity.objects.get_latest_by_template(template_id)
        if not last_version:
            return None
        return last_version.version

    @property
    def latest_version_id(self):
        template_id = self.id
        last_version = VersionedEntity.objects.get_latest_by_template(template_id)
        if not last_version:
            return None
        return last_version.id

    # TODO mark refactor
    def copy_tempalte(self, project_id, new_template_name, username):
        """复制模板集
        """
        old_show_version = ShowVersion.objects.filter(
            template_id=self.id).order_by('-updated').first()
        # 新建模板集
        new_tem = Template.objects.create(
            project_id=project_id,
            name=new_template_name,
            desc=self.desc,
            creator=username,
            updator=username,
            draft=self.draft,
            draft_time=self.draft_time,
            draft_updator=self.draft_updator,
            draft_version=self.draft_version
        )
        if not old_show_version:
            return new_tem.id, -1, -1
        old_version = VersionedEntity.objects.filter(
            id=old_show_version.real_version_id).first()
        if not old_version:
            return new_tem.id, -1, -1

        entity = old_version.get_entity()
        new_entity = {}
        for item in entity:
            item_ids = entity[item]
            if not item_ids:
                continue
            item_id_list = item_ids.split(',')
            item_ins_list = MODULE_DICT.get(
                item).objects.filter(id__in=item_id_list)
            new_item_id_list = []
            for _ins in item_ins_list:
                # 复制资源
                _ins.pk = None
                _ins.save()
                # 重命名资源名称
                _ins_name = _ins.get_name
                _ins_real_name = _ins_name.split(COPY_TEMPLATE)[0]
                # 查看已经名称的个数
                search_name = '%s%s' % (_ins_real_name, COPY_TEMPLATE)
                search_list = MODULE_DICT.get(item).objects.filter(
                    name__contains=search_name).values_list('name', flat=True)

                # 获取重命名的后缀
                _s_num_list = []
                for _s_name in set(search_list):
                    _s_num = _s_name.split(search_name)[-1]
                    try:
                        _s_num = int(_s_num)
                        _s_num_list.append(_s_num)
                    except Exception:
                        pass
                search_name_count = max(_s_num_list) + 1 if _s_num_list else 1
                new_name = '%s%s%s' % (
                    _ins_real_name, COPY_TEMPLATE, search_name_count)

                # 需要修改 config 中的name信息
                _new_config = _ins.get_config()
                _new_config_name = _new_config.get('metadata', {}).get('name')
                if _new_config_name:
                    _new_config['metadata']['name'] = new_name

                # 更新 db 中的name信息
                _ins.config = json.dumps(_new_config)
                _ins.name = new_name
                _ins.save()
                new_item_id_list.append(str(_ins.id))

            new_entity[item] = ','.join(new_item_id_list)
        # 新建version
        new_ver = VersionedEntity.objects.create(
            template_id=new_tem.id,
            entity=json.dumps(new_entity),
            last_version_id=old_version.id,
            version=get_default_version(),
            creator=username,
            updator=username,
        )
        # 新建可见版本
        new_show_ver = ShowVersion.objects.create(
            template_id=new_tem.id,
            real_version_id=new_ver.id,
            name=old_show_version.name,
            history=json.dumps([new_ver.id])
        )
        return new_tem.id, new_ver.id, new_show_ver.id

    @classmethod
    def check_resource_name(cls, project_id, resource_name, resource_id, name, version_id):
        """同一类资源的名称不能重复
        """
        # 判断新名称与老名称是否一致
        old_res = MODULE_DICT.get(resource_name).objects.filter(
            id=resource_id).first()
        if old_res:
            old_name = old_res.get_name
            if old_name == name:
                return True

        # 只校验当前版本内是否重复
        versions = VersionedEntity.objects.filter(id=version_id)
        # if resource_name[:3] == 'K8s':
        #     versions = VersionedEntity.objects.filter(id=version_id)
        # else:
        #     # 判断名称在改类资源中是否已经存在
        #     template_ids = cls.objects.filter(
        #         project_id=project_id).values_list('id', flat=True)
        #     versions = VersionedEntity.objects.filter(template_id__in=template_ids)

        pro_resource_id_list = []
        for ver_entity in versions:
            entity = ver_entity.get_entity()
            if not entity:
                continue

            item_ids = entity.get(resource_name)
            item_id_list = item_ids.split(',') if item_ids else []
            pro_resource_id_list.extend(item_id_list)

        pro_resource_id_list = set(pro_resource_id_list)

        name_exists = MODULE_DICT.get(
            resource_name).objects.filter(name=name, id__in=pro_resource_id_list).exists()
        if name_exists:
            return False
        return True


class ShowVersion(BaseModel):
    """展示给用户的版本
    """
    template_id = models.IntegerField("关联的模板 ID")
    name = models.CharField("版本名称", max_length=255)
    history = models.TextField("所有指向过的版本", default='[]')
    real_version_id = models.IntegerField("关联的VersionedEntity ID", null=True, blank=True)

    objects = ShowVersionManager()
    default_objects = models.Manager()

    def save(self, *args, **kwargs):
        # 捕获名称重复异常
        try:
            if isinstance(self.history, list):
                self.history = json.dumps(list(set(self.history)))
            super().save(*args, **kwargs)
        except IntegrityError:
            # TODO mark refactor use ValidationError not properly
            detail = {
                '版本': [_("版本号[{}]已经存在,请重新填写").format(self.name)]
            }
            raise ValidationError(detail=detail)

    def get_history(self):
        try:
            history = json.loads(self.history)
            return history
        except Exception:
            return []

    def update_real_version_id(self, real_version_id, **kwargs):
        update_params = {
            'real_version_id': real_version_id
        }
        history = self.get_history()
        history.append(real_version_id)
        update_params['history'] = history
        update_params.update(kwargs)
        self.__dict__.update(update_params)
        self.save()

    @property
    def related_template(self):
        return Template.objects.get(id=self.template_id)

    class Meta:
        index_together = ("is_deleted", "template_id")
        unique_together = ("template_id", "name")
        ordering = ('-updated',)


class VersionedEntity(BaseModel):
    """配置模板集版本信息
    entity 字段内容如下：表名：记录ID
    {
        'application': 'ApplicationID1,ApplicationID2,ApplicationID3',
        'service': 'ServiceID1,ServiceID2',
        ...
    }
    """
    template_id = models.IntegerField("关联的模板 ID")
    version = models.CharField("模板集版本号", max_length=32)
    entity = models.TextField("实体", help_text="json格式数据", blank=True, null=True)
    last_version_id = models.IntegerField("上一个版本ID", default=0)

    objects = VersionedEntityManager()

    def __str__(self):
        return f'<{self.version}/{self.template_id}/{self.last_version_id}>'

    def save(self, *args, **kwargs):
        if isinstance(self.entity, dict):
            self.entity = json.dumps(self.entity)
        super().save(*args, **kwargs)

    def get_entity(self):
        try:
            entity = json.loads(self.entity)
        except Exception:
            logger.exception(f"解析 VersionedEntity 异常\nid:{self.id}\n:entity{self.entity}")
            return {}
        return entity

    def _get_resource_id_list(self, entity, resource_name):
        resource_id_str = entity.get(resource_name, '')
        resource_id_list = resource_id_str.split(',') if resource_id_str else []
        return resource_id_list

    def get_resource_id_list(self, resource_name):
        entity = self.get_entity()
        return self._get_resource_id_list(entity, resource_name)

    def get_configmaps_by_kind(self, app_kind):
        resource_map = {
            K8S_KIND: [K8sResourceName.K8sConfigMap.value, k8s.K8sConfigMap],
            MESOS_KIND: [MesosResourceName.configmap.value, mesos.ConfigMap]
        }
        configmap_id_list = self.get_resource_id_list(resource_map[app_kind][0])
        model_class = resource_map[app_kind][1]
        return model_class.get_resources_info(configmap_id_list)

    def get_secrets_by_kind(self, app_kind):
        resource_map = {
            K8S_KIND: [K8sResourceName.K8sSecret.value, k8s.K8sSecret],
            MESOS_KIND: [MesosResourceName.secret.value, mesos.Secret]
        }
        secret_id_list = self.get_resource_id_list(resource_map[app_kind][0])
        model_class = resource_map[app_kind][1]
        return model_class.get_resources_info(secret_id_list)

    def get_k8s_services(self):
        svc_id_list = self.get_resource_id_list(K8sResourceName.K8sService.value)
        return k8s.K8sService.get_resources_info(svc_id_list)

    def get_k8s_deploys(self):
        """获取模板集版本的 Deployment 列表
        """
        deploy_id_list = self.get_resource_id_list(K8sResourceName.K8sDeployment.value)
        return k8s.K8sDeployment.get_resources_info(deploy_id_list)

    def get_mesos_apps(self):
        """获取模板集版本的 Application 列表
        """
        app_id_list = self.get_resource_id_list(MesosResourceName.application.value)
        return mesos.Application.get_resources_info(app_id_list)

    def get_mesos_deploys(self):
        """获取mesos deploys 列表
        """
        deploy_id_list = self.get_resource_id_list(MesosResourceName.deployment.value)
        return mesos.Deplpyment.get_resources_info(deploy_id_list)

    def get_k8s_svc_selector_labels(self):
        svc_id_list = self.get_resource_id_list(K8sResourceName.K8sService.value)
        label_dict = {}

        svc_qsets = k8s.K8sService.objects.filter(id__in=svc_id_list)
        for svc in svc_qsets:
            svc_name = svc.name
            selector_labels = svc.get_selector_labels()

            if selector_labels and isinstance(selector_labels, dict):
                for k, v in selector_labels.items():
                    ikey = f'{k}:{v}'
                    if ikey in label_dict:
                        label_dict[ikey].append(svc_name)
                    else:
                        label_dict[ikey] = [svc_name]

        return label_dict

    def _get_resource_config(self, is_simple):
        entity = self.get_entity()
        if not entity:
            return {}

        resource_config = {}
        for resource_name in entity:
            r_ids = entity[resource_name]
            if not r_ids:
                continue
            resource_id_list = r_ids.split(',')
            model_class = get_model_class_by_resource_name(resource_name)
            resource_config[resource_name] = model_class.get_resources_config(resource_id_list, is_simple)

        return resource_config

    def get_resource_config(self):
        """获取版本对应的所有配置信息
        """
        return self._get_resource_config(is_simple=False)

    def get_k8s_containers(self):
        entity = self.get_entity()
        if not entity:
            return []

        containers = []
        for resource_name in POD_RES_LIST:
            resource_id_list = self._get_resource_id_list(entity, resource_name)
            model_class = get_model_class_by_resource_name(resource_name)
            resource_qsets = model_class.objects.filter(id__in=resource_id_list)
            for robj in resource_qsets:
                containers.extend(robj.get_containers())

        return containers

    def get_mesos_containers(self, **kwargs):
        app_id_list = self.get_resource_id_list(MesosResourceName.application.value)
        model_class = get_model_class_by_resource_name(MesosResourceName.application.value)
        app_qsets = model_class.objects.filter(id__in=app_id_list)

        containers = []
        for app in app_qsets:
            containers.extend(app.get_containers())
        return containers

    def get_containers_from_yaml(self):
        entity = self.get_entity()
        if not entity:
            return []

        container_list = []
        for resource_name in constants.RESOURCES_WITH_POD:
            resource_id_list = self._get_resource_id_list(entity, resource_name)
            if not resource_id_list:
                continue

            resource_qsets = resfile.ResourceFile.objects.filter(id__in=resource_id_list)
            for robj in resource_qsets:
                container_list.extend(resfile.find_containers(robj.content))

        return container_list

    def get_containers(self, app_kind):
        if app_kind == K8S_KIND:
            containers = self.get_k8s_containers()
        else:
            containers = self.get_mesos_containers()

        container_list = [{'name': con.get('name'), 'image': con.get('image').split('/')[-1]}
                          for con in containers]
        return container_list

    def get_k8s_pod_resources(self):
        """获取模板集版本的 Pod 资源列表
        """
        pod_resource_map = {}
        entity = self.get_entity()
        for resource_name in POD_RES_LIST:
            resource_id_list = self._get_resource_id_list(entity, resource_name)
            if not resource_id_list:
                continue

            res_data = []
            model_class = get_model_class_by_resource_name(resource_name)
            res_qsets = model_class.objects.filter(id__in=resource_id_list)
            for robj in res_qsets:
                deploy_tag = robj.deploy_tag
                res_data.append({
                    'deploy_tag': f'{deploy_tag}|{resource_name}',
                    'deploy_name': robj.name
                })
            if res_data:
                short_name = resource_name[3:]
                pod_resource_map[short_name] = res_data

        return pod_resource_map

    @classmethod
    def update_for_new_ventity(cls, version_id, resource_name, resource_id, new_resource_id, **kwargs):
        """更新版本资源
        """
        ventity = cls.objects.get(id=version_id)
        resource_id_list = ventity.get_resource_id_list(resource_name)
        try:
            resource_id_list.remove(resource_id)  # resource_id is string type
        except Exception:
            pass
        resource_id_list.append(new_resource_id)

        entity = ventity.get_entity()
        entity[resource_name] = ','.join(resource_id_list)
        # 更新模板集版本
        new_version_entity = cls.objects.create(
            template_id=ventity.template_id,
            version=get_default_version(),
            entity=entity,
            last_version_id=ventity.id,
            **kwargs
        )
        return new_version_entity

    @classmethod
    def update_for_delete_ventity(cls, version_id, resource_name, resource_id, **kwargs):
        ventity = cls.objects.get(id=version_id)
        resource_id_list = ventity.get_resource_id_list(resource_name)
        if resource_id in resource_id_list:
            resource_id_list.remove(resource_id)

        entity = ventity.get_entity()
        entity[resource_name] = ','.join(resource_id_list)
        # 更新模板集版本
        new_version_entity = cls.objects.create(
            template_id=ventity.template_id,
            version=get_default_version(),
            entity=entity,
            last_version_id=ventity.id,
            **kwargs
        )
        return new_version_entity

    # TODO refactor

    @classmethod
    def get_application_by_deployment_id(cls, versioned_entity_id, deployment_id):
        try:
            ver_entity = cls.objects.get(id=versioned_entity_id)
        except Exception:
            raise ValidationError(_("模板版本(version_id:{})不存在").format(versioned_entity_id))
        try:
            deployment = mesos.Deplpyment.objects.get(id=deployment_id)
        except Exception:
            raise ValidationError(_("Deplpyment(id:{})不存在").format(deployment_id))

        entity = ver_entity.get_entity()
        apps = entity.get('application') if entity else None
        if not apps:
            raise ValidationError(_("模板版本(version_id:{})下没有可以关联的Application").format(versioned_entity_id))
        app_id_list = apps.split(',')
        apps = mesos.Application.objects.filter(
            id__in=app_id_list, app_id=deployment.app_id)
        if not apps:
            raise ValidationError(_("Deplpyment(id:{})没有关联的Application").format(deployment_id))
        return apps[0]

    @classmethod
    def get_k8s_service_by_statefulset_id(cls, version_id, sts_id):
        try:
            ventity = cls.objects.get(id=version_id)
        except Exception:
            raise ValidationError(_("模板版本(version_id:{})不存在").format(version_id))
        try:
            statefulset = k8s.K8sStatefulSet.objects.get(id=sts_id)
        except Exception:
            raise ValidationError(_("StatefulSet(id:{})不存在").format(sts_id))

        svc_id_list = ventity.get_resource_id_list(K8sResourceName.K8sService.value)

        if svc_id_list:
            svc = k8s.K8sService.objects.filter(id__in=svc_id_list, service_tag=statefulset.service_tag).first()
            if svc:
                return svc

        raise ValidationError(_("模板版本(version_id:{})使用了StatefulSet, 但未关联任何Service").format(version_id))

    @classmethod
    def get_related_apps_by_service(cls, versioned_entity_id, service_id):
        """获取service关联的应用信息
        """
        try:
            ver_entity = cls.objects.get(id=versioned_entity_id)
        except Exception:
            raise ValidationError(_("模板版本(version_id:{})不存在").format(versioned_entity_id))
        entity = ver_entity.get_entity()
        application_ids = entity.get('application') if entity else None
        application_id_list = application_ids.split(
            ',') if application_ids else []

        try:
            service = mesos.Service.objects.get(id=service_id)
        except Exception:
            raise ValidationError(_("Service(id:{})不存在").format(service_id))
        app_id_list = service.get_app_id_list()

        apps = mesos.Application.objects.filter(
            id__in=application_id_list, app_id__in=app_id_list)
        return apps

    def get_template_name(self):
        template_id = self.template_id
        return Template.objects.get(id=template_id).name

    # TODO mark refactor
    def get_version_all_container(self, type, project_kind, **kwargs):
        """
        project_kind: 1 (k8s); 2(mesos)
        """
        entity = self.get_entity()
        if not entity:
            return []
        # 区分容器类型
        if project_kind == 1:
            app_list = []
            for resource_name in POD_RES_LIST:
                res_ids = entity.get(resource_name, '')
                res_id_list = res_ids.split(',') if res_ids else []
                res_list = list(MODULE_DICT.get(resource_name).objects.filter(id__in=res_id_list))
                app_list.extend(res_list)
        else:
            # 应用列表
            resource_name = 'application'
            application = entity.get(resource_name, '')
            id_list = application.split(',') if application else []

            app_list = MODULE_DICT.get(resource_name).objects.filter(id__in=id_list)

            req_app_id_list = kwargs.get('req_app_id_list')
            if req_app_id_list:
                app_list = app_list.filter(app_id__in=req_app_id_list)

        if not app_list:
            return []

        container_list = []
        for app in app_list:
            containers = app.get_containers()
            for _con in containers:
                if type == "port":
                    port_list = _con.get('ports')
                    for _port in port_list:
                        if project_kind == 1:
                            container_list.append({
                                'name': _port.get('name'),
                                'containerPort': _port.get('containerPort'),
                                'id': _port.get('id')
                            })
                        else:
                            container_list.append({
                                'name': _port.get('name'),
                                'protocol': _port.get('protocol'),
                                # TODO ： 根据网络模式确定
                                'target_port': _port.get('containerPort'),
                                'id': _port.get('id')
                            })
                elif type == "base":
                    container_list.append({
                        'name': _con.get('name'),
                        'image': _con.get('image').split('/')[-1]
                    })
        return container_list

    def get_secret_info_by_k8s_ingress(self, item, item_objects):
        """k8s原生ingress需要
        """
        tls_secret_list = []
        for item_app in item_objects:
            _item_config = item_app.get_config()
            ingress_name = item_app.get_name
            # 配置项中每一个tls证书需要生成一个secret文件
            tls_list = _item_config.get('spec', {}).get('tls', [])
            for _tls in tls_list:
                cert_id = _tls.get('certId')
                if not cert_id:
                    continue

                cert_type = _tls.get('certType') or 'tls'
                secret_name = get_secret_name_by_certid(cert_id, ingress_name)
                tls_secret_list.append({
                    'id': '%s%s%s%s%s%s%s' % (item_app.id, INGRESS_ID_SEPARATOR, cert_id,
                                              INGRESS_ID_SEPARATOR, item, INGRESS_ID_SEPARATOR, cert_type),
                    "name": secret_name
                })
        return tls_secret_list

    # 实例化页面需要的模板资源列表
    def get_version_instance_resources(self):
        entity = self.get_entity()
        if not entity:
            return {}

        version_config = {}
        # 单独处理 application 和 deployment
        deployment_ids = entity.get('deployment')
        deployment_id_list = deployment_ids.split(
            ',') if deployment_ids else []
        deployment_app_id_list = mesos.Deplpyment.objects.filter(
            id__in=deployment_id_list).values_list('app_id', flat=True)

        app_config_map_list = []
        k8s_app_config_map_list = []
        app_metric_list = []
        tls_secret_list = []
        for item in entity:
            item_ids = entity[item]
            if not item_ids:
                continue
            item_id_list = item_ids.split(',')

            try:
                item_objects = MODULE_DICT.get(item).objects.filter(id__in=item_id_list)
            except AttributeError:
                logger.error(f'parse VersionedEntity(id:{self.id}) error: MODULE_DICT has no attribute {item}')
                raise

            # k8s原生ingress需要生成包含证书信息的secret
            if item in ['K8sIngress']:
                tls_secret_list = self.get_secret_info_by_k8s_ingress(item, item_objects)
            # 非标准日志采集
            elif item in ["application", "K8sDeployment", "K8sDaemonSet", "K8sJob", "K8sStatefulSet"]:
                # 模板中部分设置需要添加额外的配置文件
                for item_app in item_objects:
                    _item_config = item_app.get_config()

                    # 定义了非标准日志采集，则需要默认添加一个 configmap
                    containers = _item_config.get('spec', {}).get(
                        'template', {}).get('spec', {}).get('containers', [])
                    for _c in containers:
                        _c_name = _c.get('name')
                        # 每个 container 需要生成一个 configmap
                        log_path_list = _c.get('logPathList') or []
                        if log_path_list:
                            _confg_map = {
                                'id': '%s%s%s%s%s' % (item_app.id, APPLICATION_ID_SEPARATOR, _c_name,
                                                      APPLICATION_ID_SEPARATOR, item),
                                'name': '%s-%s-%s' % (item_app.get_name, _c_name, LOG_CONFIG_MAP_SUFFIX),
                            }
                            if item in POD_RES_LIST:
                                k8s_app_config_map_list.append(_confg_map)
                            else:
                                app_config_map_list.append(_confg_map)
                            logger.info('non-log k8s_app_config_map_list:%s' % k8s_app_config_map_list)
                            logger.info('non-log app_config_map_list:%s' % app_config_map_list)

                    web_cache = _item_config.get('webCache') or {}
                    is_metric = web_cache.get('isMetric') or False
                    metric_id_list = web_cache.get('metricIdList') or []
                    if is_metric and metric_id_list:
                        metric_list = Metric.objects.filter(
                            id__in=metric_id_list, is_deleted=False)
                        for _m in metric_list:
                            app_metric_list.append({
                                'id': '%s%s%s%s%s' % (item_app.id, APPLICATION_ID_SEPARATOR,
                                                      _m.id, APPLICATION_ID_SEPARATOR, item),
                                'name': _m.name,
                            })

            # Application 若已经被 Deployment 关联则不能再实例化
            if item == 'application':
                item_objects = item_objects.exclude(
                    app_id__in=deployment_app_id_list)

            item_config = []
            for _i in item_objects:
                item_config.append({
                    'id': _i.id,
                    'name': _i.get_name,
                })
            if item_config:
                version_config[item] = item_config

        if app_config_map_list:
            if version_config.get('configmap'):
                version_config['configmap'].extend(app_config_map_list)
            else:
                version_config['configmap'] = app_config_map_list
        if k8s_app_config_map_list:
            if version_config.get('K8sConfigMap'):
                version_config['K8sConfigMap'].extend(k8s_app_config_map_list)
            else:
                version_config['K8sConfigMap'] = k8s_app_config_map_list
        if app_metric_list:
            version_config['metric'] = app_metric_list
        if tls_secret_list:
            if version_config.get('K8sSecret'):
                version_config['K8sSecret'].extend(tls_secret_list)
            else:
                version_config['K8sSecret'] = tls_secret_list

        return version_config

    @property
    def get_version_instance_resource_ids(self):
        version_instance_resources = self.get_version_instance_resources()
        instance_entity_dict = {}
        for _r in version_instance_resources:
            _r_value = version_instance_resources[_r]
            instance_entity_dict[_r] = [_v["id"] for _v in _r_value]
        return instance_entity_dict

    def get_version_app_resource(self, category, resources_name, is_related_res=False):
        """获取应用实例化所需要的资源
        """
        instance_entity = self.get_version_instance_resources()
        new_entity = get_app_resource(
            instance_entity, category, resources_name, is_related_res, self.id)
        return new_entity

    def get_version_app_resource_ids(self, category, resources_name, is_related_res=False):
        version_instance_resources = self.get_version_app_resource(
            category, resources_name, is_related_res)
        instance_entity_dict = {}
        for _r in version_instance_resources:
            _r_value = version_instance_resources[_r]
            instance_entity_dict[_r] = [_v["id"] for _v in _r_value]
        return instance_entity_dict

    def get_lb_services_by_ids(self, service_id_list):
        service_objects = mesos.Service.objects.filter(id__in=service_id_list)

        service_list = []
        for _s in service_objects:
            if _s.is_related_lb():
                service_list.append({
                    "id": _s.id,
                    "name": _s.get_name
                })
        return service_list

    @property
    def get_lb_services(self):
        """版本中关联 lb 的service
        """
        entity = self.get_entity()
        if not entity:
            return []
        service_ids = entity.get('service')
        service_id_list = service_ids.split(',') if service_ids else []
        service_list = self.get_lb_services_by_ids(service_id_list)
        return service_list

    def get_version_ports(self, app_id_list):
        """mesos Service 页面上的可选择的关联的 Application 的 端口信息
        """
        return self.get_version_all_container(type="port", project_kind=2, **{'req_app_id_list': app_id_list})

    def get_mesos_services(self):
        svc_id_list = self.get_resource_id_list(MesosResourceName.service.value)
        return mesos.Service.get_resources_info(svc_id_list)


def get_app_resource(instance_entity, category, resources_name, is_related_res=False, version_id=''):
    """获取单个使用实例化时，需要实例化的资源
    TODO：依赖的 ConfigMap 和 Secret
    """
    category_id_list = instance_entity.get(category)
    if not category_id_list:
        return {}
    new_entity = {}
    for _c in category_id_list:
        try:
            _resource = MODULE_DICT.get(category).objects.get(id=_c['id'])
            _name = _resource.get_name
        except Exception:
            logger.exception(u"%s (id:%s)不存在" % (category, _c['id']))
            continue
        if _name == resources_name:
            new_entity[category] = [_c]
            # is_related_res=True 时，还需要添加 依赖的 ConfigMap 和 Secret
            if is_related_res:
                # TODO : 处理 k8s 的pod的资源
                related_app = None
                if category == 'application':
                    related_app = _resource
                elif category == 'deployment':
                    related_app = VersionedEntity.get_application_by_deployment_id(
                        version_id, _c['id'])
                if related_app:
                    # 查看 Application 配置信息中依赖的 configMap 和 sercret
                    configmap_name_list, secret_name_list = related_app.get_related_resource(
                        instance_entity)
                    # 处理依赖的 configmap
                    if configmap_name_list:
                        _related_configmap_list = []
                        configmap_id_list = instance_entity.get('configmap')
                        for _config_map in configmap_id_list:
                            if _config_map['name'] in configmap_name_list:
                                _related_configmap_list.append(_config_map)
                        new_entity['configmap'] = _related_configmap_list
                    # 处理依赖的 secret
                    if secret_name_list:
                        _related_secret_list = []
                        secret_id_list = instance_entity.get('secret')
                        for _secret in secret_id_list:
                            if _secret['name'] in secret_name_list:
                                _related_secret_list.append(_secret)
                        new_entity['secret'] = _related_secret_list
            break
    return new_entity
