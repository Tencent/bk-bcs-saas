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
import base64
import logging
from itertools import groupby

from django.conf import settings
from rest_framework import response, serializers, viewsets
from rest_framework.exceptions import ValidationError

from .resources import Namespace
from backend.accounts import bcs_perm
from backend.apps import constants
from backend.apps.constants import K8S_SYS_NAMESPACE, ClusterType
from backend.apps.depot.api import get_jfrog_account, get_bk_jfrog_auth
from backend.apps.instance.constants import K8S_IMAGE_SECRET_PRFIX, MESOS_IMAGE_SECRET
from backend.apps.variable.models import NameSpaceVariable
from backend.components import paas_cc
from backend.components.bcs.k8s import K8SClient
from backend.components.bcs.mesos import MesosClient
from backend.utils.error_codes import error_codes
from backend.utils.response import APIResult
from backend.activity_log import client
from backend.apps.constants import ProjectKind

logger = logging.getLogger(__name__)
K8S_PROJECT_KIND = 1
MESOS_PROJECT_KIND = 2


class NamespaceUpdateSLZ(serializers.Serializer):
    env_type = serializers.ChoiceField(
        required=False, choices=[i.value for i in constants.EnvType])
    name = serializers.RegexField(
        r'^[a-z][a-z0-9-]+$', min_length=2, max_length=30, required=False)
    cluster_id = serializers.CharField(required=False)
    ns_vars = serializers.JSONField(required=False)

    def validate_cluster_id(self, cluster_id):
        access_token = self.context['request'].user.token.access_token
        project_id = self.context['project_id']
        result = paas_cc.get_all_clusters(
            access_token, project_id, limit=constants.ALL_LIMIT)
        if result.get('code') != 0:
            raise ValidationError("校验 cluster_id 失败，%s" %
                                  result.get('message'))

        data = result['data']
        if not data or data['count'] == 0:
            raise ValidationError("cluster_id 不正确")

        for cluster in data['results']:
            if cluster_id == cluster['cluster_id']:
                return cluster_id
        raise ValidationError("cluster_id 不正确")

    def validate_name(self, name):
        """名字不能重复
        - mesos 名称全局唯一
        - k8s 同一集群下，名称唯一
        """
        # k8s 不能创建系统的命名空间
        project_kind = self.context['request'].project.kind
        if project_kind == K8S_PROJECT_KIND:
            if name in K8S_SYS_NAMESPACE:
                raise ValidationError(u"不允许创建系统命名空间[%s]" %
                                      ','.join(K8S_SYS_NAMESPACE))

        access_token = self.context['request'].user.token.access_token
        project_id = self.context['project_id']
        ns_id = self.context.get('ns_id')
        result = paas_cc.get_namespace_list(
            access_token, project_id, limit=constants.ALL_LIMIT)
        if result.get('code') != 0:
            raise ValidationError("校验名称失败, %s" % result)
        if project_kind == K8S_PROJECT_KIND:
            results = {
                str(i['id']): (i['cluster_id'], i['name'])
                for i in result['data']['results'] or []
            }
            cluster_id = self.initial_data['cluster_id']
            ns_name = results.get(ns_id)
            if (cluster_id, name) in results.values() and (cluster_id, name) != ns_name:
                raise ValidationError("同一集群，命名空间名称不能重复")
        elif project_kind == MESOS_PROJECT_KIND:
            results = {str(i['id']): i['name']
                       for i in result['data']['results'] or []}
            ns_name = results.get(ns_id)
            if name in results.values() and ns_name != name:
                raise ValidationError("命名空间名称不能重复")
        else:
            raise ValidationError("项目编排类型不正确")
        return name

    def validate(self, data):
        if not data:
            raise ValidationError("【env_type】,【name】和【cluster_id】不能同时为空")
        # 前端去掉环境类型字段，默认为 DEV
        if 'env_type' not in data:
            data['env_type'] = "dev"
        return data


class NamespaceSLZ(NamespaceUpdateSLZ):
    cluster_id = serializers.CharField(required=True)
    env_type = serializers.ChoiceField(
        choices=[i.value for i in constants.EnvType], required=False)
    # k8s同样限制长度为[2, 30]，只是为了前端显示使用
    name = serializers.RegexField(
        r'[a-z][a-z0-9-]+', min_length=2, max_length=30, required=True)


class NamespaceBase(object):
    """命名空间操作的基本方法
    其他地方也要用到，所以提取为单独的类
    """
    def create_ns_by_bcs(self, client, name, data):
        ns_config = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": name
            }
        }
        result = client.create_namespace(ns_config)
        # 通过错误消息判断 Namespace 是否已经存在，已经存在则直接进行下一步
        res_msg = result.get('message') or ''
        is_already_exists = res_msg.endswith("already exists")
        if result.get('code') != 0 and not is_already_exists:
            raise error_codes.ComponentError.f(
                "创建Namespace失败，%s, 请联系管理员解决" % result.get('message'))

    def delete_ns_by_bcs(self, client, name):
        result = client.delete_namespace(name)
        if result.get('code') != 0:
            raise error_codes.ComponentError.f(
                "创建Namespace失败，%s, 请联系管理员解决" % result.get('message'))

    def create_jforg_secret(self, client, access_token, project_id, project_code, data):
        try:
            domain_list = paas_cc.get_jfrog_domain_list(
                access_token, project_id, data['cluster_id'])
            domain_list = set(domain_list)

            # 获取项目的用户信息
            jfrog_account = get_jfrog_account(
                access_token, project_code, project_id)
            user_pwd = "%s:%s" % (jfrog_account.get(
                'user'), jfrog_account.get('password'))
            user_auth = {
                "auth": base64.b64encode(
                    user_pwd.encode(encoding="utf-8")).decode()
            }

            auth_dict = {}
            for _d in domain_list:
                if _d.startswith(settings.BK_JFROG_ACCOUNT_DOMAIN):
                    _bk_auth = get_bk_jfrog_auth(access_token, project_code, project_id)
                    auth_dict[_d] = _bk_auth
                else:
                    auth_dict[_d] = user_auth

            jfrog_auth = {
                "auths": auth_dict
            }

            jfrog_auth_bytes = bytes(json.dumps(jfrog_auth), "utf-8")
            jfrog_config = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "%s%s" % (K8S_IMAGE_SECRET_PRFIX, data['name']),
                    "namespace": data['name']
                },
                "data": {
                    ".dockerconfigjson": base64.b64encode(jfrog_auth_bytes).decode()
                },
                "type": "kubernetes.io/dockerconfigjson"
            }
            result = client.create_secret(data['name'], jfrog_config)
        except Exception as e:
            self.delete_ns_by_bcs(client, data['name'])
            logger.exception(u"获取项目仓库账号信息失败:%s" % e)
            raise ValidationError(u"获取项目仓库账号信息失败，请联系管理员解决")

        # 通过错误消息判断 包含仓库信息的secret 是否已经存在，已经存在则直接进行下一步
        res_msg = result.get('message') or ''
        is_already_exists = res_msg.endswith("already exists")

        if result.get('code') != 0 and not is_already_exists:
            self.delete_ns_by_bcs(client, data['name'])
            raise error_codes.ComponentError.f(
                "创建registry secret失败，%s, 请联系管理员解决" % result.get('message'))

    def init_namespace_by_bcs(self, access_token, project_id, project_code, data):
        """ k8s 的集群需要创建 Namespace 和 jfrog Sercret
        """
        client = K8SClient(access_token, project_id,
                           data['cluster_id'], env=None)
        name = data['name']
        # 创建 ns
        self.create_ns_by_bcs(client, name, data)
        # 创建 jfrog Sercret
        self.create_jforg_secret(client, access_token,
                                 project_id, project_code, data)

    def check_ns_image_secret(self, client, access_token, project_id, cluster_id, ns_name):
        """检查命名空间下是否已经有secret文件
        """
        params = {
            "namespace": ns_name,
            "name": MESOS_IMAGE_SECRET,
            "decode": "1",
            "field": "namespace,resourceName"
        }
        resp = client.get_secrets(params)
        # 能够在storage上查询到则说明存在
        data = resp.get('data') or []
        if data:
            return True
        return False

    def init_mesos_ns_by_bcs(self, access_token, project_id, project_code, cluster_id, ns_name):
        """新建包含仓库账号信息的sercret配置文件并下发
        """
        # 获取镜像仓库地址
        jfrog_domain = paas_cc.get_jfrog_domain(access_token, project_id, cluster_id)
        # 按项目申请仓库的账号信息

        # 判断是否为研发仓库，正式环境分为：研发仓库、生产仓库，这2个仓库的账号要分开申请
        if jfrog_domain.startswith(settings.BK_JFROG_ACCOUNT_DOMAIN):
            is_bk_jfrog = True
        else:
            is_bk_jfrog = False
        jfrog_account = get_jfrog_account(access_token, project_code, project_id, is_bk_jfrog)
        _user = jfrog_account.get('user', '')
        _pwd = jfrog_account.get('password', '')
        jfrog_config = {
            "kind": "secret",
            "metadata": {
                "name": MESOS_IMAGE_SECRET,
                "namespace": ns_name
            },
            "datas": {
                "user": {
                    "content": base64.b64encode(_user.encode(encoding="utf-8")).decode()
                },
                "pwd": {
                    "content": base64.b64encode(_pwd.encode(encoding="utf-8")).decode()
                }
            },
            "apiVersion": "v4"
        }

        # 下发secret配置文件
        client = MesosClient(access_token, project_id, cluster_id, env=None)
        result = client.create_secret(ns_name, jfrog_config)
        if result.get('code') != 0:
            client.delete_secret(ns_name, MESOS_IMAGE_SECRET)
            raise error_codes.ComponentError.f(
                "创建registry secret失败，%s, 请联系管理员解决" % result.get('message'))


class NamespaceView(NamespaceBase, viewsets.ViewSet):
    def get_ns(self, request, project_id, namespace_id):
        """获取单个命名空间的信息
        """
        access_token = request.user.token.access_token
        result = paas_cc.get_namespace(access_token, project_id, namespace_id)
        if result.get('code') != 0:
            raise error_codes.APIError.f(result.get('message', ''))
        return response.Response(result)

    def list(self, request, project_id):
        """命名空间列表
        权限控制: 必须有对应集群的使用权限
        """
        access_token = request.user.token.access_token
        valid_group_by = ['env_type', 'cluster_id', 'cluster_name']

        group_by = request.GET.get('group_by')
        cluster_id = request.GET.get('cluster_id')
        with_lb = request.GET.get('with_lb', 0)

        # 过滤有使用权限的命名空间
        perm_can_use = request.GET.get('perm_can_use')
        if perm_can_use == '1':
            perm_can_use = True
        else:
            perm_can_use = False

        # 获取全部namespace，前台分页
        result = paas_cc.get_namespace_list(
            access_token, project_id, with_lb=with_lb, limit=constants.ALL_LIMIT)
        if result.get('code') != 0:
            raise error_codes.APIError.f(result.get('message', ''))

        results = result['data']['results'] or []

        # 是否有创建权限
        perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES)
        can_create = perm.can_create(raise_exception=False)

        # 补充cluster_name字段
        cluster_ids = [i['cluster_id'] for i in results]
        cluster_list = paas_cc.get_cluster_list(
            access_token, project_id, cluster_ids).get('data') or []
        # cluster_list = bcs_perm.Cluster.hook_perms(request, project_id, cluster_list)
        cluster_dict = {i['cluster_id']: i for i in cluster_list}

        # no_vars=1 不显示变量
        no_vars = request.GET.get('no_vars')
        if no_vars == '1':
            project_var = []
        else:
            project_var = NameSpaceVariable.get_project_ns_vars(project_id)

        for i in results:
            # ns_vars = NameSpaceVariable.get_ns_vars(i['id'], project_id)
            ns_id = i['id']
            ns_vars = []
            for _var in project_var:
                _ns_values = _var['ns_values']
                _ns_value_ids = _ns_values.keys()
                ns_vars.append({
                    'id': _var['id'],
                    'key': _var['key'],
                    'name': _var['name'],
                    'value': _ns_values.get(ns_id) if ns_id in _ns_value_ids else _var['default_value'],
                })
            i['ns_vars'] = ns_vars

            if i['cluster_id'] in cluster_dict:
                i['cluster_name'] = cluster_dict[i['cluster_id']]['name']
                i['environment'] = cluster_dict[i['cluster_id']]['environment']
            else:
                i['cluster_name'] = i['cluster_id']
                i['environment'] = None

        # 添加permissions到数据中
        results = perm.hook_perms(results, perm_can_use)

        if cluster_id:
            results = filter(lambda x: x['cluster_id'] == cluster_id, results)

        if group_by and group_by in valid_group_by:
            # 分组, 排序
            results = [{'name': k,
                        'results': sorted(
                            list(v), key=lambda x: x['id'], reverse=True)} for k, v in groupby(
                sorted(results, key=lambda x: x[group_by]), key=lambda x: x[group_by])]
            if group_by == 'env_type':
                ordering = [i.value for i in constants.EnvType]
                results = sorted(
                    results, key=lambda x: ordering.index(x['name']))
            else:
                results = sorted(
                    results, key=lambda x: x['name'], reverse=True)
                # 按集群分组时，添加集群环境信息
                for r in results:
                    r_ns_list = r.get('results') or []
                    r_ns = r_ns_list[0] if r_ns_list else {}
                    r['environment'] = r_ns.get('environment', '')
                    r['environment_name'] = "正式" if r['environment'] == 'prod' else "测试"
        else:
            results = sorted(results, key=lambda x: x['id'], reverse=True)

        return APIResult(results, '取Namespace成功', permissions={'create': can_create})

    def delete_secret_for_mesos(self, access_token, project_id, cluster_id, ns_name):
        client = MesosClient(access_token, project_id, cluster_id, env=None)
        client.delete_secret(ns_name, MESOS_IMAGE_SECRET)

    def create_flow(self, request, project_id, data, perm):
        access_token = request.user.token.access_token
        project_kind = request.project.kind
        project_code = request.project.english_name
        if ClusterType.get(project_kind) == 'Kubernetes':
            # k8s 集群需要调用 bcs api 初始化数据
            self.init_namespace_by_bcs(
                access_token, project_id, project_code, data)
            has_image_secret = None
        else:
            ns_name = data['name']
            cluster_id = data['cluster_id']
            self.init_mesos_ns_by_bcs(access_token, project_id, project_code, cluster_id, ns_name)
            has_image_secret = True

        result = paas_cc.create_namespace(
            access_token,
            project_id,
            data['cluster_id'],
            data['name'],
            None,  # description 现在没有用到
            request.user.username,
            data['env_type'],
            has_image_secret)
        if result.get('code') != 0:
            if ClusterType.get(project_kind) != 'Kubernetes':
                self.delete_secret_for_mesos(access_token, project_id, cluster_id, ns_name)
            if 'Duplicate entry' in result.get('message', ''):
                message = "创建失败，namespace名称已经在其他项目存在"
            else:
                message = result.get('message', '')
            return response.Response({'code': result['code'], 'data': None, 'message': message})
        else:
            # 注册资源到权限中心
            perm.register(result['data']['id'], result['data']['name'])

        # 创建成功后需要保存变量信息
        result_data = result.get('data')
        if data.get('ns_vars') and result_data:
            ns_id = result_data.get('id')
            res, not_exist_vars = NameSpaceVariable.batch_save(
                ns_id, data['ns_vars'])
            if not_exist_vars:
                not_exist_show_msg = [f'{i["key"]}[id:{i["id"]}]' for i in not_exist_vars]
                result['message'] = f"以下变量不存在:{';'.join(not_exist_show_msg)}"
            result['data']['ns_vars'] = NameSpaceVariable.get_ns_vars(
                ns_id, project_id)
        return result

    def create(self, request, project_id, is_validate_perm=True):
        """新建命名空间
        k8s 流程：新建namespace配置文件并下发 -> 新建包含仓库账号信息的sercret配置文件并下发 -> 在paas-cc上注册
        mesos流程：新建包含仓库账号信息的sercret配置文件并下发 -> 在paas-cc上注册
        """
        serializer = NamespaceSLZ(data=request.data, context={
            'request': request, 'project_id': project_id})
        serializer.is_valid(raise_exception=True)

        data = serializer.data

        # 判断权限
        cluster_id = data['cluster_id']
        perm = bcs_perm.Namespace(request, project_id, bcs_perm.NO_RES, cluster_id)
        perm.can_create(raise_exception=is_validate_perm)

        data = serializer.data
        description = f'集群: {cluster_id}, 创建命名空间: 命名空间[{data["name"]}]'
        with client.ContextActivityLogClient(
                project_id=project_id,
                user=request.user.username,
                resource_type='namespace',
                resource=data['name'],
                description=description
        ).log_add():
            result = self.create_flow(request, project_id, data, perm)

        return response.Response(result)

    def update(self, request, project_id, namespace_id, is_validate_perm=True):
        """修改命名空间
        不允许修改命名空间信息，只能修改变量信息
        TODO: 在wesley提供集群下使用的命名空间后，允许命名空间修改名称
        """
        serializer = NamespaceUpdateSLZ(data=request.data, context={
            'request': request, 'project_id': project_id, 'ns_id': namespace_id})
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        result = {'code': 0, 'data': data, 'message': u"更新成功"}
        # 更新成功后需要保存变量信息
        if data.get('ns_vars'):
            res, not_exist_vars = NameSpaceVariable.batch_save(
                namespace_id, data['ns_vars'])
            if not_exist_vars:
                not_exist_show_msg = ['%s[id:%s]' %
                                      (i['key'], i['id']) for i in not_exist_vars]
                result['message'] = u"以下变量不存在:%s" % ";".join(
                    not_exist_show_msg)
            result['data']['ns_vars'] = NameSpaceVariable.get_ns_vars(
                namespace_id, project_id)
        return response.Response(result)

    def delete(self, request, project_id, namespace_id, is_validate_perm=True):
        # NOTE: open mesos delete namespace, when mesos api ready
        if request.project.kind == ProjectKind.MESOS.value:
            raise error_codes.NotOpen('mesos api not ready')

        access_token = request.user.token.access_token

        # perm
        perm = bcs_perm.Namespace(request, project_id, namespace_id)
        perm.can_delete(raise_exception=is_validate_perm)

        # start delete oper
        client = Namespace(access_token, project_id, request.project.kind)
        resp = client.delete(namespace_id)

        # delete ns registered perm
        perm.delete()

        return response.Response(resp)