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
import logging

from backend.components.bcs import BCSClientBase
from backend.components.utils import http_delete, http_get, http_post, http_put
from backend.utils.decorators import handle_api_not_implemented, parse_response_data
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes

STORAGE_PREFIX = "{apigw_host}/v4/storage"
SCHEDULER_PREFIX = "{apigw_host}/v4/scheduler"
METRIC_PREFIX = "{apigw_host}/v4/metric"

# service monitor 默认参数
SERVICE_MONITOR_API_VERSION = "monitor.tencent.com/v1"


logger = logging.getLogger(__name__)


class MesosClient(BCSClientBase):
    """Mesos的API"""

    @property
    def storage_host(self):
        return STORAGE_PREFIX.format(apigw_host=self.api_host)

    @property
    def scheduler_host(self):
        return SCHEDULER_PREFIX.format(apigw_host=self.api_host)

    @property
    def metric_host(self):
        """监控前缀"""
        return METRIC_PREFIX.format(apigw_host=self.api_host)

    def get_taskgroup(self, host_ip, fields=None):
        """获取mesos的taskgroup，解析出docker列表使用"""
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/taskgroup".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )

        if isinstance(host_ip, list):
            host_ip = ",".join(host_ip)

        params = {"access_token": self.access_token, "hostIp": host_ip}
        if fields:
            params["field"] = fields
        result = http_post(url, json=params)
        return result

    def create_application(self, namespace, data):
        """创建application"""
        url = "{host}/mesos/namespaces/{ns}/applications".format(host=self.scheduler_host, ns=namespace)
        kwargs = {"headers": self.headers}
        resp = http_post(url, json=data, **kwargs)
        return resp

    def update_application(self, namespace, data, params=None):
        """更新application"""
        instances = data["spec"]["instance"]
        url = "{host}/mesos/namespaces/{ns}/applications?instances={instances}".format(
            host=self.scheduler_host, ns=namespace, instances=instances
        )
        kwargs = {"headers": self.headers}
        resp = http_put(url, params=params, json=data, **kwargs)
        return resp

    def get_mesos_app_instances(self, app_name=None, namespace=None, field=None):
        """获取application详情"""
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/application".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        kwargs = {"headers": self.headers}
        # 请求参数
        params = {}
        if app_name:
            params["name"] = app_name
        if namespace:
            params["namespace"] = namespace
        if field:
            params["field"] = field

        resp = http_get(url, params=params, **kwargs)
        return resp

    def update_mesos_app_instance(self, namespace, instance_num, data):
        """更新application实例
        只能更新instance数量，建议和配置中instance数量保持一致
        """
        url = "{host}/mesos/namespaces/{ns}/applications".format(host=self.scheduler_host, ns=namespace)
        kwargs = {"headers": self.headers}
        params = {"instances": instance_num}
        resp = http_put(url, params=params, data=data, **kwargs)
        return resp

    def delete_mesos_app_instance(self, namespace, app_name, enforce=0):
        """删除application实例"""
        url = "{host}/mesos/namespaces/{ns}/applications/{app_name}".format(
            host=self.scheduler_host, ns=namespace, app_name=app_name
        )
        params = {"enforce": enforce}
        resp = http_delete(url, params=params, headers=self.headers)
        return resp

    def scale_mesos_app_instance(self, namespace, app_name, instance_num):
        """application扩缩容"""
        url = "{host}/mesos/namespaces/{ns}/applications/{app_name}/scale/{instance_num}".format(
            host=self.scheduler_host, ns=namespace, app_name=app_name, instance_num=instance_num
        )

        kwargs = {"headers": self.headers}
        resp = http_put(url, **kwargs)
        return resp

    def rollback_mesos_app_instance(self, namespace, data):
        """回滚application"""
        url = "{host}/mesos/namespaces/{ns}/applications/rollback".format(host=self.scheduler_host, ns=namespace)

        kwargs = {"headers": self.headers}
        resp = http_put(url, data=data, **kwargs)
        return resp

    def get_mesos_app_taskgroup(self, taskgroup_name=None, namespace=None, app_name=None, field=None):
        """获取taskgroup"""
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/taskgroup".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )

        # 可选参数
        params = {}
        if taskgroup_name:
            params["name"] = taskgroup_name
        if namespace:
            params["namespace"] = namespace
        if app_name:
            params["rcName"] = app_name
        if field:
            params["field"] = field

        kwargs = {"headers": self.headers}
        resp = http_post(url, json=params, **kwargs)
        return resp

    def rescheduler_mesos_taskgroup(self, namespace, app_name, taskgroup_name):
        """重新调度taskgroup
        删除然后重新拉起
        """
        url = "{host}/mesos/namespaces/{ns}/applications/{app_name}/taskgroups/{taskgroup_name}/rescheduler".format(
            host=self.scheduler_host, ns=namespace, app_name=app_name, taskgroup_name=taskgroup_name
        )

        kwargs = {"headers": self.headers}
        resp = http_put(url, **kwargs)
        return resp

    def create_configmap(self, namespace, data):
        url = "{host}/mesos/namespaces/{ns}/configmaps".format(host=self.scheduler_host, ns=namespace)

        resp = http_post(url, json=data, headers=self.headers)
        return resp

    def update_configmap(self, namespace, data):
        url = "{host}/mesos/namespaces/{ns}/configmaps".format(host=self.scheduler_host, ns=namespace)

        resp = http_put(url, json=data, headers=self.headers)
        return resp

    def delete_configmap(self, namespace, name):
        url = "{host}/mesos/namespaces/{ns}/configmaps/{name}".format(
            host=self.scheduler_host, ns=namespace, name=name
        )

        resp = http_delete(url, headers=self.headers)
        return resp

    def disable_agent(self, ip):
        """停用agent，不允许再被调度"""
        url = "{host}/mesos/agentsettings/disable".format(host=self.scheduler_host)
        params = {"ips": ip}
        resp = http_post(url, params=params, headers=self.headers)
        return resp

    def enable_agent(self, ip):
        """启用Agent"""
        url = "{host}/mesos/agentsettings/enable".format(host=self.scheduler_host)
        params = {"ips": ip}
        resp = http_post(url, params=params, headers=self.headers)
        return resp

    def create_secret(self, namespace, data):
        url = "{host}/mesos/namespaces/{ns}/secrets".format(host=self.scheduler_host, ns=namespace)
        resp = http_post(url, json=data, headers=self.headers)
        return resp

    def update_secret(self, namespace, data):
        url = "{host}/mesos/namespaces/{ns}/secrets".format(host=self.scheduler_host, ns=namespace)
        resp = http_put(url, json=data, headers=self.headers)
        return resp

    def delete_secret(self, namespace, name):
        """删除secret"""
        url = "{host}/mesos/namespaces/{ns}/secrets/{name}".format(host=self.scheduler_host, ns=namespace, name=name)

        resp = http_delete(url, headers=self.headers)
        return resp

    def create_service(self, namespace, data):
        url = "{host}/mesos/namespaces/{ns}/services".format(host=self.scheduler_host, ns=namespace)
        resp = http_post(url, json=data, headers=self.headers)
        return resp

    def update_service(self, namespace, data):
        url = "{host}/mesos/namespaces/{ns}/services".format(host=self.scheduler_host, ns=namespace)
        resp = http_put(url, json=data, headers=self.headers)
        return resp

    def delete_service(self, namespace, name):
        """删除service"""
        url = "{host}/mesos/namespaces/{ns}/services/{name}".format(host=self.scheduler_host, ns=namespace, name=name)
        resp = http_delete(url, headers=self.headers)
        return resp

    def create_deployment(self, namespace, data):
        url = "{host}/mesos/namespaces/{ns}/deployments".format(host=self.scheduler_host, ns=namespace)

        resp = http_post(url, json=data, headers=self.headers)
        return resp

    def get_deployment(self, name=None, field=None, namespace=None):
        """查询deployment"""
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/deployment".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        params = {}
        if name:
            params["name"] = name
        if field:
            params["field"] = field
        if namespace:
            params["namespace"] = namespace
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def update_deployment(self, namespace, data, params=None):
        """更新Deployment"""
        url = "{host}/mesos/namespaces/{ns}/deployments".format(host=self.scheduler_host, ns=namespace)

        resp = http_put(url, params=params, json=data, headers=self.headers)
        return resp

    def cancel_update_deployment(self, namespace, deployment_name):
        """取消更新deployment"""
        url = "{host}/mesos/namespaces/{ns}/deployments/{name}/cancelupdate".format(
            host=self.scheduler_host, ns=namespace, name=deployment_name
        )
        resp = http_put(url, headers=self.headers)
        return resp

    def pause_update_deployment(self, namespace, deployment_name):
        """暂停更新deployment"""
        url = "{host}/mesos/namespaces/{ns}/deployments/{name}/pauseupdate".format(
            host=self.scheduler_host, ns=namespace, name=deployment_name
        )

        resp = http_put(url, headers=self.headers)
        return resp

    def resume_update_deployment(self, namespace, deployment_name):
        """继续更新deployment"""
        url = "{host}/mesos/namespaces/{ns}/deployments/{name}/resumeupdate".format(
            host=self.scheduler_host, ns=namespace, name=deployment_name
        )

        resp = http_put(url, headers=self.headers)
        return resp

    def delete_deployment(self, namespace, deployment_name, enforce=0):
        """删除deployment name"""
        url = "{host}/mesos/namespaces/{ns}/deployments/{name}".format(
            host=self.scheduler_host, ns=namespace, name=deployment_name
        )
        params = {"enforce": enforce}
        resp = http_delete(url, params=params, headers=self.headers)
        return resp

    def get_events(self, params):
        """获取事件"""
        url = "{host}/events".format(host=self.storage_host)
        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def get_services(self, params):
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/service".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )

        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def get_configmaps(self, params):
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/configmap".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )

        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def get_secrets(self, params):
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/secret".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )

        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def get_endpoints(self, params):
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/endpoints".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )

        resp = http_get(url, params=params, headers=self.headers)
        return resp

    def set_metrics(self, data, cluster_type="mesos"):
        """添加监控"""
        url = "{host}/clustertype/{cluster_type}/metrics".format(host=self.metric_host, cluster_type=cluster_type)
        # 参数必须是一个列表
        if not isinstance(data, list):
            data = [data]

        resp = http_post(url, json=data, headers=self.headers)
        return resp

    def delete_metrics(self, namespace, metric_name, cluster_type="mesos"):
        """
        删除监控
        """
        # 参数必须是一个列表
        if not isinstance(metric_name, list):
            metric_name = [metric_name]
        name = ",".join(metric_name)

        url = "{host}/clustertype/{cluster_type}/clusters/{cluster_id}/namespaces/{namespace}/metrics?name={name}".format(  # noqa
            host=self.metric_host,
            cluster_type=cluster_type,
            cluster_id=self.cluster_id,
            namespace=namespace,
            name=name,
        )

        resp = http_delete(url, headers=self.headers)
        return resp

    def get_metrics(self, name, cluster_id_list):
        """"""
        url = "{host}/metrics".format(
            host=self.metric_host,
        )
        data = {"name": name, "clusterID": cluster_id_list}

        resp = http_post(url, json=data, headers=self.headers)
        return resp

    def get_application_with_post(self, name=None, namespace=None, field=None):
        """通过post请求，查询app信息"""
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/application".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        data = {}
        if name:
            data["name"] = name
        if namespace:
            data["namespace"] = namespace
        if field:
            data["field"] = field
        return http_post(url, json=data, headers=self.headers)

    def get_deployment_with_post(self, name=None, field=None, namespace=None):
        """通过post请求，查询deployment"""
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/deployment".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        data = {}
        if name:
            data["name"] = name
        if field:
            data["field"] = field
        if namespace:
            data["namespace"] = namespace
        return http_post(url, json=data, headers=self.headers)

    @parse_response_data(default_data=[])
    def get_agent_attrs(self, params=None):
        """获取节点属性"""
        url = "{host}/mesos/agentsettings".format(host=self.scheduler_host)
        return http_get(url, params=params, headers=self.headers)

    def update_agent_attrs(self, attrs):
        """批量修改/增加节点属性"""
        url = "{host}/mesos/agentsettings".format(host=self.scheduler_host)

        return http_post(url, json=attrs, headers=self.headers)

    def get_used_namespace(self):
        """获取已经使用的命名空间名称"""
        url = "{host}/query/mesos/dynamic/clusters/{cluster_id}/namespace".format(
            host=self.storage_host, cluster_id=self.cluster_id
        )
        result = http_get(url, headers=self.headers)
        return result

    def get_application_conf(self, namespace, name):
        """查询application配置"""
        url = "{host}/mesos/definition/application/{namespace}/{name}".format(
            host=self.scheduler_host, namespace=namespace, name=name
        )
        return http_get(url, headers=self.headers)

    def get_deployment_conf(self, namespace, name):
        url = "{host}/mesos/definition/deployment/{namespace}/{name}".format(
            host=self.scheduler_host, namespace=namespace, name=name
        )
        return http_get(url, headers=self.headers)

    def send_application_signal(self, namespace, name, data):
        """对指定的application下所有的running状态的taskgroup发送信息"""
        url = "{host}/mesos/namespaces/{namespace}/applications/{name}/message".format(
            host=self.scheduler_host, namespace=namespace, name=name
        )
        return http_post(url, json=data, headers=self.headers)

    def send_command(self, category, namespace, name, config):
        """发送命令"""
        url = "{host}/mesos/command/{category}/{ns}/{name}".format(
            host=self.scheduler_host, category=category, ns=namespace, name=name
        )
        return http_post(url, json=config, headers=self.headers)

    def get_command_status(self, category, namespace, name, params):
        """查询命令执行状态"""
        url = "{host}/mesos/command/{category}/{ns}/{name}".format(
            host=self.scheduler_host, category=category, ns=namespace, name=name
        )
        return http_get(url, params=params, headers=self.headers)

    def delete_command(self, category, namespace, name, params):
        """删除命令"""
        url = "{host}/mesos/command/{category}/{ns}/{name}".format(
            host=self.scheduler_host, category=category, ns=namespace, name=name
        )
        return http_delete(url, params=params, headers=self.headers)

    def get_container_exec_id(self, host_ip: str, container_id: str) -> str:
        """获取exec id"""
        url = f"{self.scheduler_host}/mesos/webconsole/create_exec"
        params = {"host_ip": host_ip}
        data = {"container_id": container_id, "cmd": ["sh"]}
        try:
            result = http_post(url, json=data, params=params, headers=self.headers)
        except Exception as error:
            logger.exception("get_container_exec_id error, %s", error)
            return None

        exec_id = result.get("Id")
        return exec_id

    def resize_container_exec(self, host_ip: str, exec_id: str, height: int, width: int) -> None:
        """设置窗口大小"""
        url = f"{self.scheduler_host}/mesos/webconsole/resize_exec"
        params = {"host_ip": host_ip}
        data = {"exec_id": exec_id, "height": height, "width": width}
        try:
            result = http_post(url, json=data, params=params, timeout=2, headers=self.headers)
            return result
        except Exception as error:
            logger.warning("resize_container_exec error, %s", error)

    def create_hpa(self, namespace, spec):
        """创建HPA"""
        url = f"{self.api_host}/v4/scheduler/mesos/crd/namespaces/{namespace}/autoscaler"
        result = http_post(url, json=spec, headers=self.headers)
        return result

    def update_hpa(self, namespace, spec):
        """更新HPA"""
        url = f"{self.api_host}/v4/scheduler/mesos/crd/namespaces/{namespace}/autoscaler"
        result = http_put(url, json=spec, headers=self.headers)
        return result

    def get_hpa(self, namespace, name):
        """获取HPA"""
        url = f"{self.api_host}/v4/scheduler/mesos/crd/namespaces/{namespace}/autoscaler/{name}"
        result = http_get(url, headers=self.headers)
        return result

    def apply_hpa(self, namespace, spec):
        """创建或者更新HPA"""
        name = spec["metadata"]["name"]
        hpa = self.get_hpa(namespace, name)
        if not hpa.get("result"):
            return self.create_hpa(namespace, spec)
        return self.update_hpa(namespace, spec)

    def delete_hpa(self, namespace, name):
        """删除HPA"""
        url = f"{self.api_host}/v4/scheduler/mesos/crd/namespaces/{namespace}/autoscaler/{name}"
        result = http_delete(url, headers=self.headers)
        return result

    def list_hpa(self, namespace=None):
        """获取HPA列表"""
        if namespace:
            url = f"{self.api_host}/v4/scheduler/mesos/crd/namespaces/{namespace}/autoscaler"
        else:
            url = f"{self.api_host}/v4/scheduler/mesos/crd/autoscaler"
        result = http_get(url, headers=self.headers)
        return result

    def _handle_custom_resource_result(self, result):
        # key `code` 存在时，认为出现了异常
        if result.get("code"):
            raise error_codes.APIError(
                f"create custom resource error, code: {result.get('code')}, message: {result.get('message')}"
            )
        return result

    def create_custom_resource(
        self, namespace, spec, group="clb.bmsf.tencent.com", apiversion="v1", plural="clbingresses"
    ):  # noqa
        """创建自定义资源
        group和apiversion对应crd中`apiVersion`
        plural: 表示类型复数，例如: clbingress, plural值为clbingresses
        """
        url = f"{self.scheduler_host}/mesos/customresources/{group}/{apiversion}/namespaces/{namespace}/{plural}"
        result = http_post(url, json=spec, headers=self.headers)
        return self._handle_custom_resource_result(result)

    def get_custom_resource(
        self, name, namespace, group="clb.bmsf.tencent.com", apiversion="v1", plural="clbingresses"
    ):
        url = f"{self.scheduler_host}/mesos/customresources/{group}/{apiversion}/namespaces/{namespace}/{plural}/{name}"  # noqa
        result = http_get(url, headers=self.headers)
        return self._handle_custom_resource_result(result)

    def delete_custom_resource(
        self, name, namespace, group="clb.bmsf.tencent.com", apiversion="v1", plural="clbingresses"
    ):
        url = f"{self.scheduler_host}/mesos/customresources/{group}/{apiversion}/namespaces/{namespace}/{plural}/{name}"  # noqa
        result = http_delete(url, headers=self.headers)
        return self._handle_custom_resource_result(result)

    def update_custom_resource(
        self, name, namespace, spec, group="clb.bmsf.tencent.com", apiversion="v1", plural="clbingresses"
    ):
        url = f"{self.scheduler_host}/mesos/customresources/{group}/{apiversion}/namespaces/{namespace}/{plural}/{name}"  # noqa
        result = http_put(url, json=spec, headers=self.headers)
        return self._handle_custom_resource_result(result)

    def get_custom_resource_by_cluster(self, group="clb.bmsf.tencent.com", apiversion="v1", plural="clbingresses"):
        url = f"{self.scheduler_host}/mesos/customresources/{group}/{apiversion}/{plural}/"
        result = http_get(url, headers=self.headers)
        return self._handle_custom_resource_result(result)

    def get_cluster_ippool(self):
        """获取集群ip资源的总览"""
        url = f"{self.storage_host}/query/mesos/dynamic/clusters/{self.cluster_id}/ippoolstatic"
        resp = http_get(url, headers=self.headers)
        if resp.get("code") != ErrorCode.NoError:
            logger.error("查询ippool失败，%s", resp.get("message"))
            return {}
        if not resp.get("data"):
            logger.error("查询ippool失败，返回数据为空")
            return {}
        # 返回的格式为数组，但只有一个值，因此，返回第一个值
        # 返回字段含义: activeip（当前已使用） +  availableip（剩余可用） + reservedip（当前保留）
        return resp["data"][0]

    def get_cluster_ippool_detail(self):
        """获取集群ip资源详情"""
        url = f"{self.storage_host}/query/mesos/dynamic/clusters/{self.cluster_id}/ippoolstaticdetail"
        resp = http_get(url, headers=self.headers)
        if resp.get("code") != ErrorCode.NoError:
            logger.error("查询ippool详情失败，%s", resp.get("message"))
            return {}
        if not resp.get("data"):
            logger.error("查询ippool详情失败，返回数据为空")
            return {}
        return resp["data"][0]

    def _get_service_monitor_url(self, namespace=None):
        """servicemonitor固定前缀"""
        if namespace:
            url = f"{self.scheduler_host}/mesos/customresources/monitor.tencent.com/v1/namespaces/{namespace}/servicemonitors"  # noqa
        else:
            url = f"{self.scheduler_host}/mesos/customresources/monitor.tencent.com/v1/servicemonitors"
        return url

    @handle_api_not_implemented(keyword="404", module="Metric管理")
    def list_service_monitor(self, namespace=None):
        """servicemonitor列表"""
        url = self._get_service_monitor_url(namespace)
        resp = http_get(url, headers=self.headers)
        return resp

    @handle_api_not_implemented(keyword="404", module="Metric管理")
    def create_service_monitor(self, namespace, spec):
        """创建servicemonitor"""
        # Mesos API Version 是BCS定制
        spec["apiVersion"] = SERVICE_MONITOR_API_VERSION
        url = self._get_service_monitor_url(namespace)
        return http_post(url, json=spec, headers=self.headers, raise_for_status=False)

    @handle_api_not_implemented(keyword="404", module="Metric管理")
    def get_service_monitor(self, namespace, name):
        """获取servicemonitor"""
        url_prefix = self._get_service_monitor_url(namespace)
        url = f"{url_prefix}/{name}"
        return http_get(url, headers=self.headers, raise_for_status=False)

    @handle_api_not_implemented(keyword="404", module="Metric管理")
    def update_service_monitor(self, namespace, name, spec):
        """更新servicemonitor"""
        # Mesos API Version 是BCS定制
        spec["apiVersion"] = SERVICE_MONITOR_API_VERSION
        url_prefix = self._get_service_monitor_url(namespace)
        url = f"{url_prefix}/{name}"
        return http_put(url, json=spec, headers=self.headers, raise_for_status=False)

    @handle_api_not_implemented(keyword="404", module="Metric管理")
    def delete_service_monitor(self, namespace, name):
        """删除servicemonitor"""
        url_prefix = self._get_service_monitor_url(namespace)
        url = f"{url_prefix}/{name}"
        return http_delete(url, headers=self.headers, raise_for_status=False)
