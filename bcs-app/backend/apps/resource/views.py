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
"""
 从Storage获取项目下的ConfigMap和Serects两种资源
"""
import base64
import copy
import datetime
import re
import logging
import json
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from django.utils.translation import ugettext_lazy as _

from backend.accounts import bcs_perm
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes
from backend.apps.application.utils import APIResponse
from backend.apps.application.base_views import BaseAPI
from backend.apps.instance.models import InstanceConfig
from backend.components import paas_cc
from backend.components.bcs import k8s, mesos
from backend.apps import constants
from backend.apps.application.constants import DELETE_INSTANCE
from backend.activity_log import client as activity_client
from backend.apps.instance.generator import GENERATOR_DICT
from backend.apps.instance.funutils import update_nested_dict, render_mako_context
from backend.apps.instance.drivers import get_scheduler_driver
from backend.apps.instance.constants import (ANNOTATIONS_UPDATE_TIME, ANNOTATIONS_UPDATOR,
                                             K8S_CONFIGMAP_SYS_CONFIG, CONFIGMAP_SYS_CONFIG, SECRET_SYS_CONFIG,
                                             K8S_SECRET_SYS_CONFIG, LABLE_TEMPLATE_ID, LABLE_INSTANCE_ID,
                                             K8S_IMAGE_SECRET_PRFIX, ANNOTATIONS_CREATOR, SOURCE_TYPE_LABEL_KEY,
                                             MESOS_IMAGE_SECRET)
from backend.apps.configuration.serializers import (ConfigMapCreateOrUpdateSLZ, SecretCreateOrUpdateSLZ,
                                                    K8sConfigMapCreateOrUpdateSLZ, K8sSecretCreateOrUpdateSLZ)
from backend.apps.configuration.models import Template
from backend.apps.network.serializers import BatchResourceSLZ
from backend.apps.application.constants import SOURCE_TYPE_MAP
from backend.utils.renderers import BKAPIRenderer
from backend.utils.basic import getitems
from backend.apps import utils as app_utils
from backend.apps.constants import ProjectKind
from backend.apps.instance import constants as inst_constants
from backend.apps.configuration.constants import MesosResourceName

logger = logging.getLogger(__name__)
DEFAULT_ERROR_CODE = ErrorCode.UnknownError
DEFAULT_SEARCH_FIELDS = ["data.metadata.labels", "data.metadata.annotations",
                         "createTime", "namespace", "resourceName"]
RE_COMPILE = re.compile(r'[^T.]+')
MESOS_VALUE = ProjectKind.MESOS.value


class ConfigMapBase:

    def k8s_configmaps(self, access_token, project_id, cluster_id, fields):
        client = k8s.K8SClient(access_token, project_id, cluster_id, env=None)
        return client.get_configmap(fields)

    def mesos_configmaps(self, access_token, project_id, cluster_id, fields):
        client = mesos.MesosClient(access_token, project_id, cluster_id, env=None)
        return client.get_configmaps(fields)

    def get_configmaps(self, request, project_id, cluster, project_kind):
        """get configmap from project and cluster
        """
        fields = ','.join(['namespace', 'resorceName'])
        k8s_mesos_map = {
            1: self.k8s_configmaps,
            2: self.mesos_configmaps
        }
        configmap_resp = k8s_mesos_map[project_kind](
            request.user.token.access_token, project_id, cluster['cluster_id'], fields)
        if configmap_resp.get('code') != ErrorCode.NoError:
            logger.error('request bcs api error, %s' % configmap_resp.get('message'))
            return []
        data = configmap_resp.get('data') or []
        skip_namespace_list = constants.K8S_SYS_NAMESPACE
        skip_namespace_list.extend(constants.K8S_COMPONENT_NAMESPACE)
        return [
            {
                'name': info['resourceName'],
                'namespace': info['namespace'],
                'cluster_id': cluster['cluster_id'],
                'cluster_name': cluster['name']
            }
            for info in data
            if info['namespace'] not in skip_namespace_list
        ]


class ResourceOperate(object):
    category = None
    mesos_cate = None
    k8s_cate = None
    # 更新相关参数
    mesos_sys_config = None
    k8s_sys_config = None
    mesos_slz = None
    k8s_slz = None
    desc = "cluster: {cluster_id}, namespace: {namespace}, delete {resource_name}: {name}"

    def delete_single_resource(self, request, project_id, project_kind, cluster_id, namespace, namespace_id, name):
        username = request.user.username
        access_token = request.user.token.access_token

        if project_kind == MESOS_VALUE:
            client = mesos.MesosClient(
                access_token, project_id, cluster_id, env=None)
            curr_func = getattr(client, "delete_%s" % self.category)
            resp = curr_func(namespace, name)
            s_cate = self.mesos_cate
        else:
            if namespace in constants.K8S_SYS_NAMESPACE:
                return {
                    "code": 400,
                    "message": _("不允许操作系统命名空间[{}]").format(','.join(constants.K8S_SYS_NAMESPACE)),
                }
            client = k8s.K8SClient(
                access_token, project_id, cluster_id, env=None)
            curr_func = getattr(client, "delete_%s" % self.category)
            resp = curr_func(namespace, name)
            s_cate = self.k8s_cate

        if resp.get("code") == ErrorCode.NoError:
            # 删除成功则更新状态
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            InstanceConfig.objects.filter(
                namespace=namespace_id,
                category=s_cate,
                name=name,
            ).update(
                creator=username,
                updator=username,
                oper_type=DELETE_INSTANCE,
                updated=now_time,
                deleted_time=now_time,
                is_deleted=True,
                is_bcs_success=True
            )
        return {
            "code": resp.get("code"),
            "message": resp.get("message"),
        }

    def delete_resource(self, request, project_id, cluster_id, namespace, name):
        username = request.user.username
        project_kind = request.project.kind

        # 检查用户是否有命名空间的使用权限
        namespace_id = app_utils.get_namespace_id(
            request.user.token.access_token, project_id, (cluster_id, namespace), cluster_id=cluster_id)
        app_utils.can_use_namespace(request, project_id, namespace_id)

        resp = self.delete_single_resource(request, project_id, project_kind,
                                           cluster_id, namespace, namespace_id, name)
        # 添加操作审计
        activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=username,
            resource_type="instance",
            resource=name,
            resource_id=0,
            extra=json.dumps({}),
            description=self.desc.format(
                cluster_id=cluster_id, namespace=namespace, resource_name=self.category, name=name)
        ).log_modify(activity_status="succeed" if resp.get("code") == ErrorCode.NoError else "failed")

        # 已经删除的，需要将错误信息翻译一下
        message = resp.get('message', '')
        is_delete_before = True if 'node does not exist' in message or 'not found' in message else False
        if is_delete_before:
            message = _("{}[命名空间:{}]已经被删除，请手动刷新数据").format(name, namespace)
        return Response({
            "code": resp.get("code"),
            "message": message,
            "data": {}
        })

    def batch_delete_resource(self, request, project_id):
        """批量删除资源
        """
        username = request.user.username
        project_kind = request.project.kind

        slz = BatchResourceSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.data['data']

        namespace_list = [(ns['cluster_id'], ns.get('namespace')) for ns in data]
        namespace_list = set(namespace_list)

        # 检查用户是否有命名空间的使用权限
        app_utils.can_use_namespaces(request, project_id, namespace_list)

        # namespace_dict format: {(cluster_id, ns_name): ns_id}
        namespace_dict = app_utils.get_ns_id_map(request.user.token.access_token, project_id)

        success_list = []
        failed_list = []
        for _d in data:
            cluster_id = _d.get('cluster_id')
            name = _d.get('name')
            namespace = _d.get('namespace')
            namespace_id = namespace_dict.get((cluster_id, namespace))
            # 删除service
            resp = self.delete_single_resource(request, project_id, project_kind,
                                               cluster_id, namespace, namespace_id, name)
            # 处理已经删除，但是storage上报数据延迟的问题
            message = resp.get('message', '')
            is_delete_before = True if 'node does not exist' in message or 'not found' in message else False
            if resp.get("code") == ErrorCode.NoError:
                success_list.append({
                    'name': name,
                    'desc': self.desc.format(
                        cluster_id=cluster_id, namespace=namespace, resource_name=self.category, name=name)
                })
            else:
                if is_delete_before:
                    message = _('已经被删除，请手动刷新数据')
                desc = self.desc.format(
                    cluster_id=cluster_id, namespace=namespace, resource_name=self.category, name=name)
                failed_list.append({
                    'name': name,
                    'desc': f'{desc}, message: {message}',
                })
        code = 0
        message = ''
        # 添加操作审计
        if success_list:
            name_list = [_s.get('name') for _s in success_list]
            desc_list = [_s.get('desc') for _s in success_list]
            message = _("以下{}删除成功:{}").format(self.category, ";".join(desc_list))
            activity_client.ContextActivityLogClient(
                project_id=project_id,
                user=username,
                resource_type="instance",
                resource=';'.join(name_list),
                resource_id=0,
                extra=json.dumps({}),
                description=";".join(desc_list)
            ).log_modify(activity_status="succeed")

        if failed_list:
            name_list = [_s.get('name') for _s in failed_list]
            desc_list = [_s.get('desc') for _s in failed_list]

            code = 4004
            message = _("以下{}删除失败:{}").format(self.category, ";".join(desc_list))
            activity_client.ContextActivityLogClient(
                project_id=project_id,
                user=username,
                resource_type="instance",
                resource=';'.join(name_list),
                resource_id=0,
                extra=json.dumps({}),
                description=message
            ).log_modify(activity_status="failed")

        return Response({
            "code": code,
            "message": message,
            "data": {}
        })

    def update_resource(self, request, project_id, cluster_id, namespace, name):
        """更新
        """
        access_token = request.user.token.access_token
        project_kind = request.project.kind

        if project_kind == MESOS_VALUE:
            # mesos 相关数据
            slz_class = self.mesos_slz
            s_sys_con = self.mesos_sys_config
            s_cate = self.mesos_cate
        else:
            if namespace in constants.K8S_SYS_NAMESPACE:
                return Response({
                    "code": 400,
                    "message": _("不允许操作系统命名空间[{}]").format(','.join(constants.K8S_SYS_NAMESPACE)),
                    "data": {}
                })
            # k8s 相关数据
            slz_class = self.k8s_slz
            s_sys_con = self.k8s_sys_config
            s_cate = self.k8s_cate

        request_data = request.data or {}
        request_data['project_id'] = project_id
        # 验证请求参数
        slz = slz_class(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.data

        config = json.loads(data['config'])
        namespace_id = data['namespace_id']
        username = request.user.username

        # 检查是否有命名空间的使用权限
        perm = bcs_perm.Namespace(request, project_id, namespace_id)
        perm.can_use(raise_exception=True)

        # 对配置文件做处理
        gparams = {
            "access_token": access_token,
            "project_id": project_id,
            "username": username
        }
        generator = GENERATOR_DICT.get(s_cate)(0, namespace_id, **gparams)
        config = generator.handle_db_config(db_config=config)
        # 获取上下文信息
        context = generator.context
        now_time = context.get('SYS_UPDATE_TIME')
        instance_id = data.get('instance_id', 0)
        context.update({
            'SYS_CREATOR': data.get('creator', ''),
            'SYS_CREATE_TIME': data.get('create_time', ''),
            'SYS_INSTANCE_ID': instance_id
        })

        # 生成配置文件
        sys_config = copy.deepcopy(s_sys_con)
        resource_config = update_nested_dict(config, sys_config)
        resource_config = json.dumps(resource_config)
        try:
            config_profile = render_mako_context(resource_config, context)
        except Exception:
            logger.exception(u"配置文件变量替换出错\nconfig:%s\ncontext:%s" %
                             (resource_config, context))
            raise ValidationError(_("配置文件中有未替换的变量"))

        config_profile = generator.format_config_profile(config_profile)

        service_name = config.get('metadata', {}).get('name')
        _config_content = {
            'name': service_name,
            'config': json.loads(config_profile),
            'context': context
        }

        # 更新db中的数据
        config_objs = InstanceConfig.objects.filter(
            namespace=namespace_id,
            category=s_cate,
            name=service_name,
        )
        if config_objs.exists():
            config_objs.update(
                creator=username,
                updator=username,
                oper_type='update',
                updated=now_time,
                is_deleted=False,
            )
            _instance_config = config_objs.first()
        else:
            _instance_config = InstanceConfig.objects.create(
                namespace=namespace_id,
                category=s_cate,
                name=service_name,
                config=config_profile,
                instance_id=instance_id,
                creator=username,
                updator=username,
                oper_type='update',
                updated=now_time,
                is_deleted=False
            )
        _config_content['instance_config_id'] = _instance_config.id
        configuration = {
            namespace_id: {
                s_cate: [_config_content]
            }
        }

        driver = get_scheduler_driver(
            access_token, project_id, configuration, request.project.kind)
        result = driver.instantiation(is_update=True)

        failed = []
        if isinstance(result, dict):
            failed = result.get('failed') or []
        # 添加操作审计
        activity_client.ContextActivityLogClient(
            project_id=project_id,
            user=username,
            resource_type="instance",
            resource=service_name,
            resource_id=_instance_config.id,
            extra=json.dumps(configuration),
            description=_("更新{}[{}]命名空间[{}]").format(
                self.category, service_name, namespace)
        ).log_modify(activity_status="failed" if failed else "succeed")

        if failed:
            return Response({
                "code": 400,
                "message": _("{}[{}]在命名空间[{}]更新失败，请联系集群管理员解决").format(self.category, service_name, namespace),
                "data": {}
            })
        return Response({
            "code": 0,
            "message": "OK",
            "data": {
            }
        })

    def handle_data(self, request, data, project_kind, s_cate, access_token,
                    project_id, cluster_id, is_decode, cluster_env, cluster_name, namespace_dict=None):
        for _s in data:
            _config = _s.get('data', {})
            annotations = _config.get(
                'metadata', {}).get('annotations', {})
            _s['creator'] = annotations.get(ANNOTATIONS_CREATOR, '')
            _s['create_time'] = _s.get('createTime', '')
            _s['update_time'] = annotations.get(
                ANNOTATIONS_UPDATE_TIME, _s['create_time'])
            _s['updator'] = annotations.get(ANNOTATIONS_UPDATOR, _s['creator'])
            _s['status'] = 'Running'

            _s['can_update'] = True
            _s['can_update_msg'] = ''
            _s['can_delete'] = True
            _s['can_delete_msg'] = ''

            _s['namespace_id'] = namespace_dict.get((cluster_id, _s['namespace'])) if namespace_dict else None
            _s['cluster_id'] = cluster_id
            _s['environment'] = cluster_env
            _s['cluster_name'] = cluster_name
            _s['name'] = _s['resourceName']

            labels = _config.get('metadata', {}).get('labels', {})
            # 获取模板集信息
            template_id = labels.get(LABLE_TEMPLATE_ID)
            instance_id = labels.get(LABLE_INSTANCE_ID)
            # 资源来源
            source_type = labels.get(SOURCE_TYPE_LABEL_KEY)
            if not source_type:
                source_type = "template" if template_id else "other"
            _s['source_type'] = SOURCE_TYPE_MAP.get(source_type)

            if project_kind == 1:
                # 处理 k8s 的系统命名空间的数据
                if _s['namespace'] in constants.K8S_SYS_NAMESPACE:
                    _s['can_update'] = _s['can_delete'] = False
                    _s['can_update_msg'] = _s['can_delete_msg'] = _("不允许操作系统命名空间")
                    continue

                # 处理平台集群和命名空间下的数据
                if _s['namespace'] in constants.K8S_PLAT_NAMESPACE and cluster_id in constants.K8S_PLAT_CLUSTER_ID:
                    _s['can_update'] = _s['can_delete'] = False
                    _s['can_update_msg'] = _s['can_delete_msg'] = _("不允许操作平台命名空间")
                    continue

                if _s['namespace'] in constants.K8S_COMPONENT_NAMESPACE:
                    _s['can_update'] = _s['can_delete'] = False
                    _s['can_update_msg'] = _s['can_delete_msg'] = _("不允许操作平台命名空间")
                    continue

            # 处理创建命名空间时生成的default-token-xxx
            if s_cate == 'K8sSecret' and _s['name'].startswith('default-token'):
                is_namespace_default_token = True
            else:
                is_namespace_default_token = False

            # 处理系统默认生成的Secret
            if s_cate == 'K8sSecret' and _s['name'] == '%s%s' % (K8S_IMAGE_SECRET_PRFIX, _s['namespace']):
                is_k8s_image_sercret = True
            else:
                is_k8s_image_sercret = False

            is_mesos_image_sercret = False
            if s_cate == MesosResourceName.secret.value \
                    and _s['name'] in [MESOS_IMAGE_SECRET, inst_constants.OLD_MESOS_IMAGE_SECRET]:
                is_mesos_image_sercret = True

            if is_k8s_image_sercret or is_mesos_image_sercret or is_namespace_default_token:
                _s['can_update'] = _s['can_delete'] = False
                _s['can_update_msg'] = _s['can_delete_msg'] = _("不允许操作系统数据")
                continue

            if template_id:
                try:
                    template_id = int(template_id)
                    instance_id = int(instance_id)
                except Exception:
                    template_id = 0
                    instance_id = 0
            else:
                # 非模板集创建，可以删除但是不可以更新
                _s['can_update'] = False
                _s['can_update_msg'] = _("不是由模板实例化生成，无法更新")

            _s['instance_id'] = instance_id

            # 更新的数据解码内容
            if is_decode and _s['can_update']:
                # 1. k8s Secret base64 解码内容
                if s_cate == 'K8sSecret':
                    _d = _config.get('data')
                    for _key in _d:
                        if _d[_key]:
                            try:
                                _d[_key] = base64.b64decode(
                                    _d[_key]).decode("utf-8")
                            except Exception:
                                pass
                elif s_cate in ['secret', 'configmap']:
                    _d = _config.get('datas')
                    for _key in _d:
                        _type = _d[_key].get('type')
                        if _type != 'http' and _d[_key]['content']:
                            try:
                                _d[_key]['content'] = base64.b64decode(
                                    _d[_key]['content']).decode("utf-8")
                            except Exception:
                                pass

        # 兼容 k8s & mesos 数据格式
        data = data_handler(data)
        # 检查是否用命名空间的使用权限
        perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES)
        data = perm.hook_perms(data, ns_id_flag='namespace_id', cluster_id_flag='cluster_id', ns_name_flag='namespace')


class ConfigMaps(viewsets.ViewSet, BaseAPI, ResourceOperate):
    def get_configmaps_by_cluster_id(self, request, params, project_id, cluster_id, project_kind=MESOS_VALUE):

        access_token = request.user.token.access_token
        search_fields = copy.deepcopy(DEFAULT_SEARCH_FIELDS)

        if project_kind == MESOS_VALUE:
            search_fields.append("data.datas")
            params.update({
                "field": ",".join(search_fields)
            })
            client = mesos.MesosClient(
                access_token, project_id, cluster_id, env=None)
            resp = client.get_configmaps(params)
        else:
            search_fields.append("data.data")
            params.update({
                "field": ",".join(search_fields)
            })
            client = k8s.K8SClient(
                access_token, project_id, cluster_id, env=None)
            resp = client.get_configmap(params)

        if resp.get("code") != ErrorCode.NoError:
            logger.error(u"bcs_api error: %s" % resp.get("message", ""))
            return resp.get("code", DEFAULT_ERROR_CODE), resp.get("message", _("请求出现异常!"))
        data = resp.get("data") or []
        # data = data_handler(resp.get("data") or [], project_kind)
        return 0, data

    def get(self, request, project_id):
        """ 获取项目下所有的ConfigMap """
        # 获取kind
        project_kind = request.project.kind
        if project_kind not in [info[0] for info in constants.ProjectKind.get_choices()]:
            raise error_codes.CheckFailed(_("项目编排类型不正确"))

        cluster_dicts = self.get_project_cluster_info(request, project_id)
        cluster_data = cluster_dicts.get('results', {}) or {}

        data = []
        params = dict(request.GET.items())
        s_cate = 'configmap' if project_kind == MESOS_VALUE else 'K8sConfigMap'
        access_token = request.user.token.access_token
        is_decode = request.GET.get('decode')
        is_decode = True if is_decode == '1' else False

        # get project namespace info
        namespace_dict = app_utils.get_ns_id_map(access_token, project_id)

        for cluster_info in cluster_data:
            cluster_id = cluster_info.get('cluster_id')
            # 当参数中集群ID存在时，判断集群ID匹配成功后，继续后续逻辑
            if params.get('cluster_id') and params['cluster_id'] != cluster_id:
                continue
            cluster_env = cluster_info.get('environment')
            code, cluster_configmaps = self.get_configmaps_by_cluster_id(
                request, params, project_id, cluster_id, project_kind=project_kind)
            # 单个集群错误时，不抛出异常信息
            if code != ErrorCode.NoError:
                continue
            self.handle_data(request, cluster_configmaps, project_kind, s_cate,
                             access_token, project_id, cluster_id,
                             is_decode, cluster_env, cluster_info.get('name', ''), namespace_dict=namespace_dict)
            data += cluster_configmaps

        # 按时间倒序排列
        data.sort(key=lambda x: x.get('createTime', ''), reverse=True)

        return APIResponse({
            "code": ErrorCode.NoError,
            "data": {
                "data": data,
                "length": len(data)
            },
            "message": "ok"
        })

    def delete_configmap(self, request, project_id, cluster_id, namespace, name):
        self.category = 'configmap'
        self.mesos_cate = 'configmap'
        self.k8s_cate = 'K8sConfigMap'
        return self.delete_resource(
            request, project_id, cluster_id, namespace, name)

    def batch_delete_configmaps(self, request, project_id):
        self.category = 'configmap'
        self.mesos_cate = 'configmap'
        self.k8s_cate = 'K8sConfigMap'
        return self.batch_delete_resource(request, project_id)

    def update_configmap(self, request, project_id, cluster_id, namespace, name):
        self.category = 'configmap'
        self.mesos_cate = 'configmap'
        self.k8s_cate = 'K8sConfigMap'
        # 更新相关参数
        self.mesos_sys_config = CONFIGMAP_SYS_CONFIG
        self.k8s_sys_config = K8S_CONFIGMAP_SYS_CONFIG
        self.mesos_slz = ConfigMapCreateOrUpdateSLZ
        self.k8s_slz = K8sConfigMapCreateOrUpdateSLZ
        return self.update_resource(request, project_id, cluster_id, namespace, name)


class ConfigMapListView(ConfigMapBase, viewsets.ViewSet):
    render_classes = (BKAPIRenderer,)

    def get_cluster_list(self, request, project_id):
        cluster_resp = paas_cc.get_all_clusters(request.user.token.access_token, project_id)
        if cluster_resp.get('code') != ErrorCode.NoError:
            raise error_codes.APIError.f(cluster_resp.get('message'))
        cluster_data = cluster_resp.get('data') or {}
        return cluster_data.get('results') or []

    def exist_list(self, request, project_id):
        """exist configmap list
        NOTE: perm is ignore in the stage
        """
        project_kind = request.project.kind
        cluster_data = self.get_cluster_list(request, project_id)
        project_configmap_list = []
        for cluster in cluster_data:
            configmap_list = self.get_configmaps(request, project_id, cluster, project_kind)
            project_configmap_list.extend(configmap_list)
        return Response({'data': project_configmap_list, 'code': ErrorCode.NoError})


class Secrets(viewsets.ViewSet, BaseAPI, ResourceOperate):
    def get_secrets_by_cluster_id(self, request, params, project_id, cluster_id, project_kind=MESOS_VALUE):
        """查询secrets
        """
        access_token = request.user.token.access_token
        search_fields = copy.deepcopy(DEFAULT_SEARCH_FIELDS)

        if project_kind == MESOS_VALUE:
            search_fields.append("data.datas")
            params.update({
                "field": ",".join(search_fields)
            })
            client = mesos.MesosClient(
                access_token, project_id, cluster_id, env=None)
            resp = client.get_secrets(params)
        else:
            search_fields.append("data.data")
            params.update({
                "field": ",".join(search_fields)
            })
            client = k8s.K8SClient(
                access_token, project_id, cluster_id, env=None)
            resp = client.get_secret(params)

        if resp.get("code") != ErrorCode.NoError:
            logger.error(u"bcs_api error: %s" % resp.get("message", ""))
            return resp.get("code", DEFAULT_ERROR_CODE), resp.get("message", _("请求出现异常!"))
        data = resp.get("data") or []
        # data = data_handler(resp.get("data") or [], project_kind)
        return 0, data

    def get(self, request, project_id):
        """ 获取项目下所有的secrets """
        # 获取kind
        flag, project_kind = self.get_project_kind(request, project_id)
        if not flag:
            return project_kind

        cluster_dicts = self.get_project_cluster_info(request, project_id)
        cluster_data = cluster_dicts.get('results', {}) or {}

        data = []
        params = dict(request.GET.items())
        s_cate = 'secret' if project_kind == MESOS_VALUE else 'K8sSecret'
        access_token = request.user.token.access_token
        is_decode = request.GET.get('decode')
        is_decode = True if is_decode == '1' else False
        # get project namespace info
        namespace_dict = app_utils.get_ns_id_map(request.user.token.access_token, project_id)

        for cluster_info in cluster_data:
            cluster_id = cluster_info.get('cluster_id')
            # 当参数中集群ID存在时，判断集群ID匹配成功后，继续后续逻辑
            if params.get('cluster_id') and params['cluster_id'] != cluster_id:
                continue
            cluster_env = cluster_info.get('environment')
            code, cluster_secrets = self.get_secrets_by_cluster_id(
                request, params, project_id, cluster_id, project_kind=project_kind)
            # 单个集群错误时，不抛出异常信息
            if code != ErrorCode.NoError:
                continue
            self.handle_data(request, cluster_secrets, project_kind, s_cate,
                             access_token, project_id, cluster_id,
                             is_decode, cluster_env, cluster_info.get('name', ''), namespace_dict=namespace_dict)
            data += cluster_secrets

        # 按时间倒序排列
        data.sort(key=lambda x: x.get('createTime', ''), reverse=True)
        return APIResponse({
            "code": ErrorCode.NoError,
            "data": {
                "data": data,
                "length": len(data)
            },
            "message": "ok"
        })

    def delete_secret(self, request, project_id, cluster_id, namespace, name):
        self.category = 'secret'
        self.mesos_cate = 'secret'
        self.k8s_cate = 'K8sSecret'
        return self.delete_resource(request, project_id, cluster_id, namespace, name)

    def batch_delete_secrets(self, request, project_id):
        self.category = 'secret'
        self.mesos_cate = 'secret'
        self.k8s_cate = 'K8sSecret'
        return self.batch_delete_resource(request, project_id)

    def update_secret(self, request, project_id, cluster_id, namespace, name):
        self.category = 'secret'
        self.mesos_cate = 'secret'
        self.k8s_cate = 'K8sSecret'
        # 更新相关参数
        self.mesos_sys_config = SECRET_SYS_CONFIG
        self.k8s_sys_config = K8S_SECRET_SYS_CONFIG
        self.mesos_slz = SecretCreateOrUpdateSLZ
        self.k8s_slz = K8sSecretCreateOrUpdateSLZ
        return self.update_resource(request, project_id, cluster_id, namespace, name)


class Endpoints(BaseAPI):
    def get(self, request, project_id, cluster_id, namespace, name):
        """ 获取项目下所有的endpoints """
        # 获取kind
        flag, project_kind = self.get_project_kind(request, project_id)
        if not flag:
            return project_kind

        access_token = request.user.token.access_token
        params = {
            "name": name,
            "namespace": namespace
        }
        if project_kind == MESOS_VALUE:
            client = mesos.MesosClient(
                access_token, project_id, cluster_id, env=None)
            resp = client.get_endpoints(params)
        else:
            client = k8s.K8SClient(
                access_token, project_id, cluster_id, env=None)
            resp = client.get_endpoints(params)

        if resp.get("code") != ErrorCode.NoError:
            return APIResponse({
                "code": resp.get("code", DEFAULT_ERROR_CODE),
                "message": resp.get("message", _("请求出现异常!"))
            })

        return APIResponse({
            "code": ErrorCode.NoError,
            "data": resp.get("data"),
            "message": "ok"
        })


def data_handler(data):
    ret_data = []
    for info in data:
        if 'createTime' in info:
            info["createTime"] = ' '.join(
                RE_COMPILE.findall(info["createTime"])[:2])
        # mesos configmap/secret获取的是datas中的数据
        info_datas = getitems(info, ['data', 'datas'], {})
        if info_datas:
            info['data']['datas'] = dict(sorted(info_datas.items(), key=lambda x: x[0]))
        # k8s configmap/secret获取的是data中的数据
        info_data = getitems(info, ['data', 'data'], {})
        if info_data:
            info['data']['data'] = dict(sorted(info_data.items(), key=lambda x: x[0]))
        ret_data.append(info)

    return ret_data