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
import base64
import copy
import json
import logging

from django.conf import settings
from django.utils.functional import cached_property
from kubernetes import client
from kubernetes.client.rest import ApiException

from backend.components.bcs import BCSClientBase
from backend.components.utils import http_delete, http_get, http_patch, http_post, http_put
from backend.utils.errcodes import ErrorCode
from backend.utils.exceptions import ComponentError

logger = logging.getLogger(__name__)


STORAGE_PREFIX = "{apigw_host}/v4/storage"
SCHEDULER_PREFIX = "{apigw_host}/v4/scheduler"
K8S_SCHEDULER_PREFIX = "{apigw_host}/v4/scheduler/k8s"
REST_PREFIX = "{apigw_host}/rest/clusters"

HTTP_KWARGS = {
    'raise_for_status': True
}


class K8SClient(BCSClientBase):
    """K8S Client
    """

    @cached_property
    def context(self):
        """BCS API Context信息
        """
        context = {}
        cluster_info = self.query_cluster()
        context.update(cluster_info)
        credentials = self.get_client_credentials(cluster_info['id'])
        context.update(credentials)
        return context

    @cached_property
    def k8s_raw_client(self):
        configure = client.Configuration()
        configure.verify_ssl = False
        configure.host = f"{self._bcs_server_host}{self.context['server_address_path']}".rstrip('/')
        configure.api_key = {"authorization": f"Bearer {self.context['user_token']}"}
        api_client = client.ApiClient(configure)
        return api_client

    @property
    def hpa_client(self):
        api_client = client.AutoscalingV2beta2Api(self.k8s_raw_client)
        return api_client

    @property
    def version(self):
        """获取k8s版本, 使用git_version字段
        """
        _client = client.VersionApi(self.k8s_raw_client)
        code = _client.get_code()
        return code.git_version

    @property
    def storage_host(self):
        return STORAGE_PREFIX.format(apigw_host=self.api_host)

    @property
    def scheduler_host(self):
        return K8S_SCHEDULER_PREFIX.format(apigw_host=self.api_host)

    @property
    def rest_host(self):
        return REST_PREFIX.format(apigw_host=self.api_host)

    def get_namespace(self, params=None):
        """获取namesapce，计算数量使用
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/namespace'.format(
            host=self.storage_host, cluster_id=self.cluster_id)
        result = http_get(url, headers=self.headers, params=params)
        return result

    def get_pod(self, host_ips=None, field=None, extra=None, params=None):
        """获取pod，获取docker列表使用
        根据label中不定key的过滤，需要使用extra字段
        比如要过滤data.metadata.labels.app为nginx，则需要如下操作
        filter_data = {"data.metadata.labels.app": "nginx"}
        data_json = json.dumps(filter_data)
        base64.b64encode(data_json)
        """
        _params = {}

        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/pod'.format(
            host=self.storage_host, cluster_id=self.cluster_id)

        if params:
            _params.update(params)
        if host_ips:
            _params['hostIp'] = ','.join(host_ips)
        if field:
            _params["field"] = field
        if extra:
            _params["extra"] = extra

        result = http_get(url, params=_params, headers=self.headers)
        return result

    def get_hostname_by_ip(self, ips=None):
        """通过ip查询到名称
        如果ip为空，返回cluster下的所有ip和name
        """
        url = "{host}/nodes".format(host=self.scheduler_host)
        result = http_get(url, headers=self.headers)
        ret_data = {}
        if result["result"]:
            for info in result["data"]["items"]:
                ip_info = info["status"]["addresses"]

                ret_data[ip_info[0]["address"]] = ip_info[1]["address"]

        return ret_data

    def disable_agent(self, ip):
        """停用，禁止被调度
        """
        ip_data = self.get_hostname_by_ip(ips=[ip])
        if not ip_data or not ip_data.get(ip):
            return {"code": ErrorCode.UnknownError, "message": u"没有查询到IP对应的hostname"}
        url = '{host}/nodes/{name}'.format(
            host=self.scheduler_host, name=ip_data[ip]
        )
        data = {"spec": {"unschedulable": True}}
        headers = copy.deepcopy(self.headers)
        headers['Content-Type'] = 'application/strategic-merge-patch+json'
        result = http_patch(url, json=data, headers=headers)
        return result

    def enable_agent(self, ip):
        """启用agent
        """
        ip_data = self.get_hostname_by_ip(ips=[ip])
        if not ip_data:
            return {"code": ErrorCode.UnknownError, "message": u"没有查询到IP对应的hostname"}
        url = '{host}/nodes/{name}'.format(
            host=self.scheduler_host, name=ip_data[ip]
        )
        data = {"spec": {"unschedulable": False}}
        headers = copy.deepcopy(self.headers)
        headers['Content-Type'] = 'application/strategic-merge-patch+json'
        result = http_patch(url, json=data, headers=headers)
        return result

    def get_service(self, params):
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/service'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def get_configmap(self, params):
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/configmap'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def get_secret(self, params):
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/secret'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def get_endpoints(self, params):
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/endpoints'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def update_deployment(self, namespace, deployment_name, data):
        """更新deployment
        包含滚动升级和扩缩容
        """
        url = '{host}/namespaces/{namespace}/deployments/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=deployment_name
        )
        resp = http_put(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_deployment(self, namespace, deployment_name):
        """删除deployment
        """
        url = '{host}/namespaces/{namespace}/deployments/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=deployment_name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def create_deployment(self, namespace, data):
        """创建deployment
        """
        url = '{host}/namespaces/{namespace}/deployments'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def get_deployment(self, params):
        """查询deployment
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/deployment'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def create_daemonset(self, namespace, data):
        """创建deamonset
        """
        url = '{host}/namespaces/{namespace}/daemonsets'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_daemonset(self, namespace, name):
        """删除deamonset
        """
        url = '{host}/namespaces/{namespace}/daemonsets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def update_daemonset(self, namespace, name, data):
        """更新daemonset
        """
        url = '{host}/namespaces/{namespace}/daemonsets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_put(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def get_daemonset(self, params):
        """查询daemonset
        TODO: 现阶段daemonset还没有上报到storage,接口还不可用
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/daemonset'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def create_statefulset(self, namespace, data):
        """创建statefulset
        """
        url = '{host}/namespaces/{namespace}/statefulsets'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def update_statefulset(self, namespace, name, data):
        """更新statefulset
        """
        url = '{host}/namespaces/{namespace}/statefulsets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name

        )
        resp = http_put(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_statefulset(self, namespace, name):
        """删除statefulset
        """
        url = '{host}/namespaces/{namespace}/statefulsets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def get_statefulset(self, params):
        """查询statefulset
        # TODO: 同样需要上报到storage
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/statefulset'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def create_job(self, namespace, data):
        """创建job
        """
        url = '{host}/namespaces/{namespace}/jobs'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def update_job(self, namespace, name, data):
        """更新job
        """
        url = '{host}/namespaces/{namespace}/jobs/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_put(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_job(self, namespace, name):
        """删除job
        """
        url = '{host}/namespaces/{namespace}/jobs/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def get_job(self, params):
        """查询job
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/job'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def create_node_labels(self, ip, labels):
        """添加节点标签
        """
        ip_data = self.get_hostname_by_ip(ips=[ip])
        if not ip_data or not ip_data.get(ip):
            return {"code": ErrorCode.UnknownError, "message": u"没有查询到IP对应的hostname"}
        url = '{host}/nodes/{name}'.format(
            host=self.scheduler_host, name=ip_data[ip]
        )
        data = {"metadata": {"labels": labels}}
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/strategic-merge-patch+json"
        result = http_patch(url, json=data, headers=headers)
        return result

    def get_node_detail(self, ip):
        """获取节点详细配置
        """
        ip_data = self.get_hostname_by_ip(ips=[ip])
        if not ip_data or not ip_data.get(ip):
            return {"code": ErrorCode.UnknownError, "message": u"没有查询到IP对应的hostname"}
        url = '{host}/nodes/{name}'.format(
            host=self.scheduler_host, name=ip_data[ip]
        )
        result = http_get(url, headers=self.headers)
        return result

    def create_service(self, namespace, data):
        """创建service
        """
        url = '{host}/namespaces/{namespace}/services'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def update_service(self, namespace, name, data):
        """更新service
        """
        url = '{host}/namespaces/{namespace}/services/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_put(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_service(self, namespace, name):
        """删除service
        """
        url = '{host}/namespaces/{namespace}/services/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def create_configmap(self, namespace, data):
        """创建configmap
        """
        url = '{host}/namespaces/{namespace}/configmaps'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def update_configmap(self, namespace, name, data):
        """更新configmap
        """
        url = '{host}/namespaces/{namespace}/configmaps/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_put(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_configmap(self, namespace, name):
        """删除configmap
        """
        url = '{host}/namespaces/{namespace}/configmaps/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def create_secret(self, namespace, data):
        """创建secrets
        """
        url = '{host}/namespaces/{namespace}/secrets'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def update_secret(self, namespace, name, data):
        """更新secrets
        """
        url = '{host}/namespaces/{namespace}/secrets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_put(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_secret(self, namespace, name):
        """删除secrets
        """
        url = '{host}/namespaces/{namespace}/secrets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def create_namespace(self, data):
        """创建namespaces
        """
        url = '{host}/namespaces'.format(
            host=self.scheduler_host
        )
        resp = http_post(url, json=data, headers=self.headers)
        return resp

    def delete_namespace(self, name):
        """删除namespaces
        """
        url = '{host}/namespaces/{name}'.format(
            host=self.scheduler_host,
            name=name
        )
        resp = http_delete(url, headers=self.headers)
        return resp

    def get_rs(self, params):
        """查询rs
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/replicaset'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def scale_instance(self, namespace, name, instance_num):
        """扩缩容
        """
        url = '{host}/k8s/namespaces/{namespace}/deployments/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        headers = self.headers
        headers["Content-Type"] = "application/strategic-merge-patch+json"
        data = {"spec": {"replicas": int(instance_num)}}
        resp = http_patch(url, json=data, headers=headers)
        return resp

    def delete_rs(self, namespace, name):
        """删除rs
        """
        url = '{host}/namespaces/{namespace}/replicasets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_pod(self, namespace, name):
        """删除pod
        """
        url = '{host}/namespaces/{namespace}/pods/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def patch_deployment(self, namespace, name, params):
        """针对deployment的patch操作
        """
        url = '{host}/namespaces/{namespace}/deployments/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        headers = self.headers
        headers["Content-Type"] = "application/strategic-merge-patch+json"
        resp = http_patch(url, json=params, headers=headers)
        return resp

    def patch_job(self, namespace, name, params):
        """针对job的patch操作
        """
        url = '{host}/namespaces/{namespace}/jobs/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        headers = self.headers
        headers["Content-Type"] = "application/strategic-merge-patch+json"
        resp = http_patch(url, json=params, headers=headers)
        return resp

    def patch_daemonset(self, namespace, name, params):
        """针对daemonset的patch操作
        """
        url = '{host}/namespaces/{namespace}/daemonsets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        headers = self.headers
        headers["Content-Type"] = "application/strategic-merge-patch+json"
        resp = http_patch(url, json=params, headers=headers)
        return resp

    def patch_statefulset(self, namespace, name, params):
        """针对statefulset的patch操作
        """
        url = '{host}/namespaces/{namespace}/statefulsets/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        headers = self.headers
        headers["Content-Type"] = "application/strategic-merge-patch+json"
        resp = http_patch(url, json=params, headers=headers)
        return resp

    def get_extra_encode(self, name):
        """查询 rs/pod 的参数组装
        """
        extra = '{"data.metadata.ownerReferences.name": "%s"}' % name
        return base64.b64encode(extra.encode(encoding="utf-8")).decode()

    def get_pods_by_upper_res(self, namespace, name):
        """通过rs/StatefulSet/job/DaemonSet 查询pod信息
        """
        extra_encode = self.get_extra_encode(name)
        params = {
            "extra": extra_encode,
            "field": "resourceName,namespace",
            "namespace": namespace
        }
        pod_res = self.get_pod(params=params)
        logger.info("k8s_deep_delete 查询[ns:%s,name:%s, extra:%s]pod:%s" % (
            namespace, name, extra_encode, pod_res))

        if pod_res.get("code") != 0:
            logger.error("k8s_deep_delete 查询[ns:%s,name:%s]pod出错:%s" % (
                namespace, name, pod_res.get('message', '')))
        pod_data = pod_res.get('data') or []
        pod_name_list = []
        for _pod in pod_data:
            _pod_name = _pod.get('resourceName')
            pod_name_list.append(_pod_name)
        return pod_name_list

    def deep_delete_deployment(self, namespace, name):
        """删除Deployment，级联删除rs&pod
        """
        # 1. 查询rs
        extra_encode = self.get_extra_encode(name)
        rs_res = self.get_rs(
            {"extra": extra_encode, "field": "resourceName,namespace", "namespace": namespace})

        logger.info("k8s_deep_delete 查询[ns:%s,name:%s]rs:%s" % (
            namespace, name, rs_res))
        if rs_res.get("code") != 0:
            logger.error("k8s_deep_delete 查询[ns:%s,name:%s]rs出错:%s" % (
                namespace, name, rs_res.get('message', '')))

        rs_name_lit = []
        pod_name_list = []
        rs_data = rs_res.get("data") or []
        for _rs in rs_data:
            _rs_name = _rs.get('resourceName')
            rs_name_lit.append(_rs_name)

            # 2. 查询pod 信息
            _pod_name_list = self.get_pods_by_upper_res(namespace, _rs_name)
            pod_name_list.extend(_pod_name_list)

        err_msg = []
        # 3. 删除 Deployment
        deploy_res = self.delete_deployment(namespace, name)
        if deploy_res.get('code') != 0:
            logger.error("k8s_deep_delete delete_deployment [ns:%s,name:%s]出错:%s" % (
                namespace, name, deploy_res.get('message', '')))
            if "not found" not in deploy_res.get('message', ''):
                err_msg.append(deploy_res.get('message', ''))
        # 3. 删除rs
        for _r_name in rs_name_lit:
            del_rs_res = self.delete_rs(namespace, _r_name)
            logger.info("k8s_deep_delete delete_rs [ns:%s,name:%s]:%s" % (
                namespace, _r_name, del_rs_res))

            if del_rs_res.get('code') != 0:
                logger.error("k8s_deep_delete delete_rs [ns:%s,name:%s]出错:%s" % (
                    namespace, _r_name, del_rs_res.get('message', '')))
                if "not found" not in del_rs_res.get('message', ''):
                    err_msg.append(del_rs_res.get('message', ''))

        # 4. 删除 pods
        for _pod_name in pod_name_list:
            del_pod_res = self.delete_pod(namespace, _pod_name)
            logger.info("k8s_deep_delete delete_pod [ns:%s,name:%s]:%s" % (
                namespace, _pod_name, del_pod_res))

            if del_pod_res.get('code') != 0:
                logger.error("k8s_deep_delete delete_pod [ns:%s,name:%s]出错:%s" % (
                    namespace, _pod_name, del_pod_res.get('message', '')))
                if "not found" not in del_pod_res.get('message', ''):
                    err_msg.append(del_pod_res.get('message', ''))

        if err_msg:
            raise ComponentError(';'.join(err_msg))

    def deep_delete_daemonset(self, namespace, name):
        # 查询pod 信息
        pod_name_list = self.get_pods_by_upper_res(namespace, name)

        result = self.delete_daemonset(namespace, name)
        err_msg = []
        if result.get('code') != 0:
            if "not found" not in result.get('message', ''):
                err_msg.append(result.get('message', ''))

        # 删除 pods
        for _pod_name in pod_name_list:
            del_pod_res = self.delete_pod(namespace, _pod_name)
            if del_pod_res.get('code') != 0:
                logger.error("k8s_deep_delete delete_pod [ns:%s,name:%s]出错:%s" % (
                    namespace, _pod_name, del_pod_res.get('message', '')))
                if "not found" not in del_pod_res.get('message', ''):
                    err_msg.append(del_pod_res.get('message', ''))
        if err_msg:
            raise ComponentError(';'.join(err_msg))

    def deep_delete_job(self, namespace, name):
        # 查询pod 信息
        pod_name_list = self.get_pods_by_upper_res(namespace, name)

        result = self.delete_job(namespace, name)
        err_msg = []
        if result.get('code') != 0:
            if "not found" not in result.get('message', ''):
                err_msg.append(result.get('message', ''))

        # 删除 pods
        for _pod_name in pod_name_list:
            del_pod_res = self.delete_pod(namespace, _pod_name)
            if del_pod_res.get('code') != 0:
                logger.error("k8s_deep_delete delete_pod [ns:%s,name:%s]出错:%s" % (
                    namespace, _pod_name, del_pod_res.get('message', '')))
                if "not found" not in del_pod_res.get('message', ''):
                    err_msg.append(del_pod_res.get('message', ''))
        if err_msg:
            raise ComponentError(';'.join(err_msg))

    def deep_delete_statefulset(self, namespace, name):
        # 查询pod 信息
        pod_name_list = self.get_pods_by_upper_res(namespace, name)

        result = self.delete_statefulset(namespace, name)
        err_msg = []
        if result.get('code') != 0:
            if "not found" not in result.get('message', ''):
                err_msg.append(result.get('message', ''))

        # 删除 pods
        for _pod_name in pod_name_list:
            del_pod_res = self.delete_pod(namespace, _pod_name)
            if del_pod_res.get('code') != 0:
                logger.error("k8s_deep_delete delete_pod [ns:%s,name:%s]出错:%s" % (
                    namespace, _pod_name, del_pod_res.get('message', '')))
                if "not found" not in del_pod_res.get('message', ''):
                    err_msg.append(del_pod_res.get('message', ''))
        if err_msg:
            raise ComponentError(';'.join(err_msg))

    def create_ingress(self, namespace, data):
        """创建 ingress
        """
        url = '{host}/namespaces/{namespace}/ingresses'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def update_ingress(self, namespace, name, data):
        """更新 ingress
        """
        url = '{host}/namespaces/{namespace}/ingresses/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_put(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def delete_ingress(self, namespace, name):
        """删除 ingress
        """
        url = '{host}/namespaces/{namespace}/ingresses/{name}'.format(
            host=self.scheduler_host,
            namespace=namespace,
            name=name
        )
        resp = http_delete(url, headers=self.headers, **HTTP_KWARGS)
        return resp

    def get_deployment_with_post(self, data):
        """通过post方法，查询deployment
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/deployment'.format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        return http_post(url, json=data, headers=self.headers)

    def get_daemonset_with_post(self, data):
        """通过post方法，查询daemonset
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/daemonset'.format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        return http_post(url, json=data, headers=self.headers)

    def get_job_with_post(self, data):
        """通过post方法，查询job
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/job'.format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        return http_post(url, json=data, headers=self.headers)

    def get_statefulset_with_post(self, data):
        """通过post方法，查询statefulset
        """
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/statefulset'.format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        return http_post(url, json=data, headers=self.headers)

    def get_ingress(self, params):
        url = '{host}/query/k8s/dynamic/clusters/{cluster_id}/ingress'.format(
            host=self.storage_host,
            cluster_id=self.cluster_id
        )
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def create_serviceaccounts(self, namespace, data):
        """创建 serviceaccounts
        """
        url = '{host}/namespaces/{namespace}/serviceaccounts'.format(
            host=self.scheduler_host,
            namespace=namespace
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def create_clusterrolebindings(self, namespace, data):
        """创建 ClusterRoleBinding
        """
        url = '{host}/clusterrolebindings'.format(
            host=self.scheduler_host
        )
        resp = http_post(url, json=data, headers=self.headers, **HTTP_KWARGS)
        return resp

    def get_used_namespace(self):
        """获取已经使用的命名空间名称
        """
        params = {"used": 1}
        return self.get_namespace(params=params)

    def query_cluster(self):
        """获取bcs_cluster_id, identifier
        """
        url = f'{self.rest_host}/bcs/query_by_id/'
        params = {
            'access_token': self.access_token,
            'project_id': self.project_id,
            'cluster_id': self.cluster_id
        }
        result = http_get(url, params=params, raise_for_status=False)
        return result

    def register_cluster(self):
        url = f'{self.rest_host}/bcs/'

        data = {
            'id': self.cluster_id,
            'project_id': self.project_id,
            'access_token': self.access_token
        }

        params = {'access_token': self.access_token}
        # 已经创建的会返回400, code_name: CLUSTER_ALREADY_EXISTS
        result = http_post(url, json=data, params=params, raise_for_status=False)

        return result

    def get_client_credentials(self, bcs_cluster_id: str) -> dict:
        """获取证书, user_token, server_address_path
        """
        url = f'{self.rest_host}/{bcs_cluster_id}/client_credentials'

        params = {'access_token': self.access_token}

        result = http_get(url, params=params, raise_for_status=False)
        return result

    def get_register_tokens(self, bcs_cluster_id: str) -> dict:
        url = f'{self.rest_host}/{bcs_cluster_id}/register_tokens'

        params = {'access_token': self.access_token}

        result = http_get(url, params=params, raise_for_status=False)
        return result

    def create_register_tokens(self, bcs_cluster_id: str) -> dict:
        url = f'{self.rest_host}/{bcs_cluster_id}/register_tokens'

        params = {'access_token': self.access_token}
        headers = {'content-type': 'application/json'}

        # 已经创建的会返回500, code_name: CANNOT_CREATE_RTOKEN
        result = http_post(url, params=params, headers=headers, raise_for_status=False)
        return result

    def list_hpa(self, namespace=None):
        """获取hpa
        - namespace 为空则获取全部
        """
        try:
            # _preload_content 设置为True, 修复kubernetes condition 异常
            if namespace:
                resp = self.hpa_client.list_namespaced_horizontal_pod_autoscaler(namespace, _preload_content=False)
            else:
                resp = self.hpa_client.list_horizontal_pod_autoscaler_for_all_namespaces(_preload_content=False)
            data = json.loads(resp.data)
        except Exception as error:
            logger.exception("list hpa error, %s", error)
            data = {}
        return data

    def get_hpa(self, namespace, name):
        return self.hpa_client.read_namespaced_horizontal_pod_autoscaler(name, namespace)

    def create_hpa(self, namespace, spec):
        """创建HPA
        """
        # _preload_content 设置为True, 修复kubernetes condition 异常
        return self.hpa_client.create_namespaced_horizontal_pod_autoscaler(namespace, spec, _preload_content=False)

    def update_hpa(self, namespace, name, spec):
        """修改HPA
        """
        return self.hpa_client.patch_namespaced_horizontal_pod_autoscaler(name, namespace, spec)

    def delete_hpa(self, namespace, name):
        try:
            return self.hpa_client.delete_namespaced_horizontal_pod_autoscaler(name, namespace)
        except client.rest.ApiException as error:
            # 404 资源未找到, 直接返回
            if error.status == 404:
                return

            logger.error('delete hpa error: %s', error)
            raise

    def apply_hpa(self, namespace, spec):
        """部署HPA
        """
        name = spec['metadata']['name']
        try:
            self.get_hpa(namespace, name)
        except client.rest.ApiException as error:
            if error.status == 404:
                result = self.create_hpa(namespace, spec)
                logger.info('hpa not found, create a new hpa, %s', result)
                return result
            else:
                logger.error('get hpa error: %s', error)
                raise error
        except Exception as error:
            logger.exception('get hpa exception: %s', error)
        else:
            logger.info('hpa found, create a new hpa, %s, %s', namespace, spec)
            return self.update_hpa(namespace, name, spec)
