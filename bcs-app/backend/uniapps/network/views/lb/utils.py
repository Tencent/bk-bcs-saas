# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import copy
import json
import logging

from django.utils.translation import ugettext_lazy as _

from backend.components.bcs.mesos import MesosClient
from backend.container_service.clusters.base import utils as cluster_resource
from backend.utils.decorators import parse_response_data
from backend.utils.errcodes import ErrorCode
from backend.utils.error_codes import error_codes

from . import constants as lb_constants

logger = logging.getLogger(__name__)


class MesosLBConfig:
    def __init__(self, access_token, project_id, cluster_id, lb):
        self.access_token = access_token
        self.project_id = project_id
        self.cluster_id = cluster_id
        self.lb = lb

    def _service_config(self):
        """组装要下发的service配置"""
        svc_conf = copy.deepcopy(lb_constants.MESOS_LB_SERVICE)
        svc_conf["metadata"].update({"name": self.lb.name, "namespace": self.lb.namespace})
        svc_conf["spec"]["selector"].update({"loadbalancer": self.lb.name})
        return svc_conf

    def _args(self, data):
        args = [
            data["forward_mode"],
            "--group",
            data["related_service_label"],
        ]
        # 获取zk
        zk_conf = cluster_resource.get_cc_zk_config(self.access_token, self.project_id, self.cluster_id)
        args += ["--zk", zk_conf["bcs_zookeeper"]]
        # 获取clusterzk，格式<编号>.<cluster_id>.bcscustom.com:2181 (多个地址逗号,分隔)
        # 这里编号的数量和master的数量一致
        masters = cluster_resource.get_cluster_masters(self.access_token, self.project_id, self.cluster_id)
        cluster_zk_conf = [f"{i}.{self.cluster_id.lower()}.bcscustom.com:2181" for i in range(1, len(masters) + 1)]
        args += [
            "--clusterzk",
            ",".join(cluster_zk_conf),
            "--zkpath",
            f"/etc/cluster/mesos/{self.cluster_id}/exportservice",
            "--bcszkaddr",
            zk_conf["bcs_zookeeper"],
            "--clusterid",
            self.cluster_id,
        ]
        return args

    def _image_path(self, data):
        """添加image"""
        # 使用用户自定义的镜像地址
        if data["use_custom_image_url"]:
            return f"{data['image_url']}:{data['image_tag']}"

        # 通过集群获取对应的平台domain
        repo_domain = cluster_resource.get_cc_repo_domain(self.access_token, self.project_id, self.cluster_id)
        return f"{repo_domain.rstrip('/')}/{data['image_url'].lstrip('/')}:{data['image_tag']}"

    def _update_containers(self, deploy_conf, data):
        # 添加args
        container_conf = deploy_conf["spec"]["template"]["spec"]["containers"][0]
        container_conf["args"] = self._args(data)
        container_conf["resources"] = data["resources"]
        container_conf["configmaps"] = data["configmaps"]
        container_conf["image"] = self._image_path(data)

        # 如果用户启用镜像凭证，则需要填写image pull user和image pull password
        if data["use_custom_imagesecret"]:
            container_conf["imagePullUser"] = data["image_pull_user"]
            container_conf["imagePullPasswd"] = data["image_pull_password"]

        # 如果网络模式为bridge时，添加hostport和containerport
        if data["network_mode"] == "BRIDGE":
            container_conf["ports"] = [
                {
                    "name": "lb-port",
                    "hostPort": data["host_port"],
                    "containerPort": data["container_port"],
                    "protocol": "TCP",
                }
            ]
        deploy_conf["spec"]["template"]["spec"]["containers"] = [container_conf]

    def _deployment_config(self):
        """组装deployment的配置"""
        data = json.loads(self.lb.data_dict)
        deploy_conf = copy.deepcopy(lb_constants.MESOS_LB_DEPLOYMENT)
        deploy_conf["metadata"].update({"name": self.lb.name, "namespace": self.lb.namespace})
        # 添加资源限制
        deploy_conf["constraint"] = data["constraint"]
        # labels中的loadbalancer和对应的service的一致
        deploy_conf["metadata"]["labels"] = {"loadbalancer": self.lb.name}
        deploy_conf["spec"]["instance"] = data["instance_num"]
        # 向labels添加ip信息，格式为: io.tencent.bcs.netsvc.requestip.x: 127.0.0.1
        # NOTE: io.tencent.bcs.netsvc.requestip.x 中 x 支持从0开始
        deploy_conf["spec"]["template"]["metadata"]["labels"] = {
            f"io.tencent.bcs.netsvc.requestip.{index}": ip for index, ip in enumerate(data["ip_list"])
        }
        # 添加container信息
        self._update_containers(deploy_conf, data)

        deploy_conf["spec"]["template"]["spec"].update(
            {
                "networkMode": data["network_mode"] if data["network_mode"] != "CUSTOM" else data["custom_value"],
                "networkType": data["network_type"],
            }
        )

        return deploy_conf


@parse_response_data()
def create_mesos_service(config, access_token=None, project_id=None, cluster_id=None, client=None):
    if not client:
        client = MesosClient(access_token, project_id, cluster_id, None)
    return client.create_service(config["metadata"]["namespace"], config)


def delete_mesos_service(namespace, name, access_token=None, project_id=None, cluster_id=None, client=None):
    if not client:
        client = MesosClient(access_token, project_id, cluster_id, None)
    return client.delete_service(namespace, name)


def create_mesos_deployment(config, access_token=None, project_id=None, cluster_id=None, client=None):
    if not client:
        client = MesosClient(access_token, project_id, cluster_id, None)
    return client.create_deployment(config["metadata"]["namespace"], config)


def delete_mesos_deployment(namespace, name, access_token=None, project_id=None, cluster_id=None, client=None):
    if not client:
        client = MesosClient(access_token, project_id, cluster_id, None)
    resp = client.delete_deployment(namespace, name)
    if resp.get("code") != ErrorCode.NoError and "not exist" not in resp.get("message"):
        raise error_codes.APIError(_("删除Mesos deployment失败，{}").format(resp.get("message")))


def deploy_mesos_lb(access_token, project_id, cluster_id, svc_conf, deploy_conf):
    """创建lb
    - 创建service，如果失败，则终止；如果成功，继续创建deployment
    - 创建deployment，如果失败，则需要删除service
    """
    client = MesosClient(access_token, project_id, cluster_id, None)
    # 创建service
    create_mesos_service(svc_conf, client=client)

    # 创建deployment
    resp = create_mesos_deployment(deploy_conf, client=client)
    if resp.get("code") != ErrorCode.NoError:
        # 删除service
        delete_mesos_service(svc_conf["metadata"]["namespace"], svc_conf["metadata"]["name"], client=client)
        raise error_codes.APIError(_("创建Mesos deployment失败，{}").format(resp.get("message")))


def stop_mesos_lb(access_token, project_id, cluster_id, namespace, name):
    """停止lb
    删除对应deployment和service
    """
    client = MesosClient(access_token, project_id, cluster_id, None)
    # 删除service
    delete_mesos_service(namespace, name, client=client)
    # 删除deployment
    delete_mesos_deployment(namespace, name, client=client)


def get_deployment(namespace, name, access_token=None, project_id=None, cluster_id=None, client=None):
    if not client:
        client = MesosClient(access_token, project_id, cluster_id, None)
    field = ["data.application", "data.status", "data.application_ext", "data.message"]
    resp = client.get_deployment(name=name, namespace=namespace, field=",".join(field))
    if resp.get("code") != ErrorCode.NoError and "not exist" not in resp.get("message"):
        raise error_codes.APIError(_("查询Mesos deployment异常，{}").format(resp.get("message")))
    return resp["data"]


def get_application(namespace, names, access_token=None, project_id=None, cluster_id=None, client=None):
    if not client:
        client = MesosClient(access_token, project_id, cluster_id, None)
    resp = client.get_mesos_app_instances(app_name=names, namespace=namespace, field="data.status,data.message")
    if resp.get("code") != ErrorCode.NoError and "not exist" not in resp.get("message"):
        raise error_codes.APIError(_("查询Mesos application异常，{}").format(resp.get("message")))
    return resp["data"]


def get_app_names_by_deployment(deployment):
    app_name_list = [deployment["data"]["application"]["name"]]
    if deployment["data"].get("application_ext"):
        app_name_list.append(deployment["data"]["application_ext"]["name"])
    return app_name_list


def get_mesos_lb_status_detail(access_token, project_id, cluster_id, namespace, name, op_status, lb_obj=None):
    client = MesosClient(access_token, project_id, cluster_id, None)
    lb_status_detail = {
        "status": op_status,
        "deployment_status": "",
        "deployment_message": "",
        "application_status": "",
        "application_message": "",
    }
    # 查询deployment
    deployment = get_deployment(namespace, name, client=client)
    # 未部署时，直接返回
    if op_status == lb_constants.MESOS_LB_STATUS.NOT_DEPLOYED.value and not deployment:
        return lb_status_detail
    # 针对删除操作时，如果deployment数据为空，认为已经删除
    if op_status == lb_constants.MESOS_LB_STATUS.STOPPING.value and not deployment:
        lb_status_detail["status"] = lb_constants.MESOS_LB_STATUS.STOPPED.value
        # 兼容处理
        if lb_obj:
            lb_obj.update_status(lb_constants.MESOS_LB_STATUS.STOPPED.value)
        return lb_status_detail

    # 如果有空，直接返回，并记录日志
    if not deployment:
        logger.error(f"查询Mesos deployment为空，cluster_id:{cluster_id},namespace:{namespace},name:{name}")
        return lb_status_detail

    deployment = deployment[0]
    # 更新deployment状态
    lb_status_detail.update(
        {"deployment_status": deployment["data"]["status"], "deployment_message": deployment["data"]["message"]}
    )
    app_name_list = get_app_names_by_deployment(deployment)
    # 查询application
    application = get_application(namespace, app_name_list, client=client)
    if not application:
        return lb_status_detail
    # 更新状态
    application = application[0]
    application_status = application["data"]["status"]
    lb_status_detail.update(
        {"application_status": application_status, "application_message": application["data"]["message"]}
    )
    # 如果是部署中，则更新为DEPLOYED
    if op_status == lb_constants.MESOS_LB_STATUS.DEPLOYING.value:
        if application_status in lb_constants.MESOS_APP_STABLE_STATUS:
            lb_status_detail["status"] = lb_constants.MESOS_LB_STATUS.DEPLOYED.value
            if lb_obj:
                lb_obj.update_status(lb_constants.MESOS_LB_STATUS.DEPLOYED.value)

    return lb_status_detail
