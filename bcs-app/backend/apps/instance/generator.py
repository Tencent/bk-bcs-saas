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
生成配置文件
DONE:
- 配置文件中 添加 namespace 相关的变量
- 配置文件中 添加 系统默认的配置

TODO：
"""
import uuid
import re
import datetime
import base64
import logging
import copy
import json
import shlex
from urllib.parse import urlparse
from collections import OrderedDict

from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from backend.components import paas_cc
from backend.components.ticket import TicketClient
from backend.apps.configuration.models import (MODULE_DICT, VersionedEntity,
                                               get_pod_qsets_by_tag, get_k8s_container_ports, CATE_SHOW_NAME,
                                               get_secret_name_by_certid)
from backend.apps.configuration.constants import NUM_VAR_PATTERN
from backend.apps.instance.funutils import update_nested_dict, render_mako_context
from backend.apps.instance.constants import (
    APPLICATION_SYS_CONFIG, DEPLPYMENT_SYS_CONFIG, SEVICE_SYS_CONFIG, CONFIGMAP_SYS_CONFIG,
    SECRET_SYS_CONFIG, LABEL_SERVICE_NAME, SEVICE_WEIGHT_LABEL_PREFIX, ANNOTATIONS_WEB_CACHE,
    LOG_CONFIG_MAP_SUFFIX, LOG_CONFIG_MAP_KEY_SUFFIX, LOG_CONFIG_MAP_PATH_PRFIX, LOG_CONFIG_MAP_APP_LABEL,
    APPLICATION_ID_SEPARATOR, LABLE_CONTAINER_SELECTOR_LABEL, K8S_INGRESS_SYS_CONFIG, K8S_LOG_ENV,
    K8S_CUSTOM_LOG_ENV_KEY, MESOS_CUSTOM_LOG_LABEL_KEY, LABLE_METRIC_SELECTOR_LABEL, API_VERSION)
from backend.apps.metric.models import Metric
from backend.apps.constants import ClusterType
from backend.apps.datalog.utils import get_data_id_by_project_id, create_and_start_non_standard_data_flow
from backend.apps.instance.constants import (K8S_SECRET_SYS_CONFIG, K8S_CONFIGMAP_SYS_CONFIG, K8S_SEVICE_SYS_CONFIG,
                                             K8S_DEPLPYMENT_SYS_CONFIG, K8S_DAEMONSET_SYS_CONFIG, K8S_JOB_SYS_CONFIG,
                                             K8S_STATEFULSET_SYS_CONFIG, K8S_RESOURCE_UNIT, K8S_ENV_KEY,
                                             K8S_IMAGE_SECRET_PRFIX, LABEL_MONITOR_LEVEL, LABEL_MONITOR_LEVEL_DEFAULT,
                                             MESOS_IMAGE_SECRET, INGRESS_ID_SEPARATOR, MESOS_MODULE_NAME,
                                             K8S_MODULE_NAME)
from backend.utils.func_controller import get_func_controller
from backend.apps.instance.utils_pub import get_cluster_version
from backend.apps.ticket.models import TlsCert
from backend.apps.instance.resources.utils import handle_number_var
from backend.apps.instance import constants as instance_constants

logger = logging.getLogger(__name__)
HANDLED_NUM_VAR_PATTERN = re.compile(r"%s}" % NUM_VAR_PATTERN)
mesos_res_mapping = OrderedDict()
k8s_res_mapping = OrderedDict()


class ProfileGenerator:
    resource_name = None
    resource_sys_config = None

    def __init__(self, resource_id, namespace_id, is_validate=True, **params):
        self.is_validate = is_validate
        self.resource_id = resource_id
        self.metric_id = 0
        self.namespace_id = namespace_id
        self.params = params
        self.lb_info = params.get('lb_info', {})
        self.project_id = params.get('project_id')
        self.access_token = params.get('access_token')
        self.version = params.get('version')
        self.version_id = params.get('version_id')
        self.template_id = params.get('template_id')
        self.is_preview = params.get('is_preview') or False
        self.has_image_secret = params.get('has_image_secret') or False

        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.context = {
            'SYS_TEMPLATE_ID': params.get("template_id"),
            'SYS_VERSION_ID': params.get("version_id"),
            'SYS_VERSION': params.get("version"),
            'LABLE_VERSION': params.get('version'),
            'SYS_INSTANCE_ID': params.get("instance_id"),
            'SYS_PROJECT_ID': params.get("project_id"),
            'SYS_OPERATOR': params.get('username'),
            'SYS_CREATOR': params.get('username'),
            'SYS_UPDATOR': params.get('username'),
            'SYS_CREATE_TIME': now_time,
            'SYS_UPDATE_TIME': now_time,
        }
        # 命名空间相关的变量，在入口处统一获取
        ns_context = params.get('context') or {}
        if not ns_context:
            self.get_ns_variable()
        else:
            self.context.update(ns_context)
        self.cluster_version = params.get('cluster_version')
        if not self.cluster_version:
            cluster_id = self.context['SYS_CLUSTER_ID']
            self.cluster_version = get_cluster_version(self.access_token, self.project_id, cluster_id)

        self.resource_show_name = ''
        self.resource = None

    def handle_db_config(self, db_config):
        """二次处理db中的配置信息
        """
        return db_config

    def get_db_config(self):
        # metric 单独处理
        if self.resource_name == 'metric':
            name_list = str(self.resource_id).split(APPLICATION_ID_SEPARATOR)
            application_id = name_list[0]
            metric_id = name_list[1]
            resourse_type = name_list[2]
            self.metric_id = metric_id
            return self.handle_db_config(application_id, metric_id, resourse_type)
        # Application 中非标准日志采集时默认的 configmap
        is_non_standard_log = True if str(self.resource_id).find(APPLICATION_ID_SEPARATOR) >= 0 else False
        if self.resource_name in ['configmap', 'K8sConfigMap'] and is_non_standard_log:
            name_list = str(self.resource_id).split(APPLICATION_ID_SEPARATOR)
            application_id = name_list[0]
            container_name = name_list[1]
            resourse_type = name_list[2]
            log_config = self.handle_application_log_config(
                application_id, container_name, resourse_type)
            return self.handle_db_config(log_config)
        # k8s ingress 生成的 secret
        is_k8s_ingress_srt = True if str(self.resource_id).find(INGRESS_ID_SEPARATOR) >= 0 else False
        if self.resource_name in ['K8sSecret'] and is_k8s_ingress_srt:
            name_list = str(self.resource_id).split(INGRESS_ID_SEPARATOR)
            cert_id = name_list[1]
            ingress_id = name_list[0]
            ingress_type = name_list[2]
            cert_type = name_list[3]
            srt_config = self.handle_k8s_ingress_srt(cert_id, ingress_id, ingress_type, cert_type)
            return self.handle_db_config(srt_config)

        try:
            self.resource = MODULE_DICT.get(
                self.resource_name).objects.get(id=self.resource_id)
        except Exception:
            raise ValidationError('{prefix_msg}{res_name}(id:{res_id}){suffix_msg}'.format(
                prefix_msg=_("参数"),
                res_name=self.resource_name,
                res_id=self.resource_id,
                suffix_msg=_("不存在")
            ))
        self.resource_show_name = self.resource.name
        orgin_db_config = self.resource.config
        # 将用户输入的配置文件内容中的变量替换, 预览时不替换由前端替换
        if not self.is_preview:
            variable_dict = self.params.get('variable_dict')
            try:
                orgin_db_config = render_mako_context(
                    orgin_db_config, variable_dict)
            except Exception as e:
                logger.exception(f"配置文件变量替换出错\nconfig:{orgin_db_config}\ncontext:{variable_dict}")
                raise ValidationError('{}[{}]'.format(_("配置文件中变量异常"), e))

        # 将用户的配置文件内容转成 json
        try:
            orgin_db_config = json.loads(orgin_db_config)
        except Exception:
            logger.exception("解析配置文件异常:%s" % orgin_db_config)
            raise ValidationError(_("配置文件格式错误"))
        db_config = self.handle_db_config(orgin_db_config)
        return db_config

    def update_config_name(self, resource_config):
        """实例化后的名称与模板集中的名称保持一致
        """
        return resource_config

    def get_resource_config(self):
        db_config = self.get_db_config()
        sys_config = copy.deepcopy(self.resource_sys_config)
        return update_nested_dict(db_config, sys_config)

    def get_ns_variable(self):
        """获取命名空间相关的变量信息
        """
        # 获取命名空间的信息
        resp = paas_cc.get_namespace(
            self.access_token, self.project_id, self.namespace_id)
        if resp.get('code') != 0:
            raise ValidationError('{}(namespace_id:{}):{}'.format(
                _("查询命名空间的信息出错"), self.namespace_id, resp.get('message')
            ))
        data = resp.get('data')
        self.context['SYS_CLUSTER_ID'] = data.get('cluster_id')
        self.context['SYS_NAMESPACE'] = data.get('name')
        self.has_image_secret = data.get('has_image_secret')
        # 获取镜像地址
        jfrog_domain = paas_cc.get_jfrog_domain(
            self.access_token, self.project_id, self.context['SYS_CLUSTER_ID'])
        self.context['SYS_JFROG_DOMAIN'] = jfrog_domain

        bcs_context = get_bcs_context(self.access_token, self.project_id)
        self.context.update(bcs_context)

    def format_config_profile(self, config_profile):
        return config_profile

    def check_configmap_exist(self, resource_config, namespace):
        """check configmap exist in the namespace
        """
        # get web cache
        web_cache = resource_config.get('webCache') or {}
        volumes = web_cache.get('volumes') or []
        # check volumes and namespace exist
        if not (volumes and namespace):
            return
        for volume in volumes:
            # configMap type
            if volume.get('type') != 'configMap':
                continue
            if volume.get('is_exist') and namespace != volume.get('namespace'):
                raise ValidationError('{prefix_msg}: {ns}({ns_name}){msg}configmap{source}'.format(
                    prefix_msg=_("实例化检查错误"), ns=_("命名空间"), ns_name=namespace,
                    msg=_("下无法关联"), source=volume.get('source')
                ))

    def get_config_profile(self):
        resource_config = self.get_resource_config()
        # check volume for configmap
        self.check_configmap_exist(resource_config, self.context.get('SYS_NAMESPACE'))
        # 前端的缓存数据储存到备注中
        resource_config = handle_webcache_config(resource_config)
        new_config = self.update_config_name(resource_config)
        new_config = json.dumps(new_config)
        if not self.is_preview:
            variable_dict = self.params.get('variable_dict')
            self.context.update(variable_dict)
        try:
            config_profile = render_mako_context(new_config, self.context)
        except Exception as e:
            logger.exception(u"配置文件变量替换出错\nconfig:%s\ncontext:%s" %
                             (new_config, self.context))
            raise ValidationError('{}[{}]'.format(_("配置文件中变量异常"), e))

        config_profile = self.format_config_profile(config_profile)
        return config_profile

    def handle_application_log_config(self, application_id, container_name, resourse_type):
        """Application 中非标准日志采集
        """
        # 获取业务的 dataid
        cc_app_id = self.context['SYS_CC_APP_ID']

        application = MODULE_DICT.get(resourse_type).objects.get(id=application_id)
        self.resource_show_name = '%s-%s-%s' % (
            application.name, container_name, LOG_CONFIG_MAP_SUFFIX)
        # 从Application 中获取日志路径
        _item_config = application.get_config()
        containers = _item_config.get('spec', {}).get(
            'template', {}).get('spec', {}).get('containers', [])
        init_containers = _item_config.get('spec', {}).get(
            'template', {}).get('spec', {}).get('initContainers', [])

        log_path_list = []
        for con_list in [init_containers, containers]:
            for _c in con_list:
                _c_name = _c.get('name')
                if _c_name == container_name:
                    log_path_list = _c.get('logPathList') or []
                    break

        if not log_path_list:
            return {}

        # 生成 configmap 的内容
        not_standard_data_id = self.context['SYS_NON_STANDARD_DATA_ID']
        inners = []
        for log_path in log_path_list:
            inners.append({
                "logpath": log_path,
                "dataid": not_standard_data_id,
                "selectors": []
            })
        log_content = {
            "inners": inners,
            "mounts": []
        }

        log_key = '%s%s' % (application.name, LOG_CONFIG_MAP_KEY_SUFFIX)
        log_config = {
            "kind": "configmap",
            "metadata": {
                "name": self.resource_show_name
            }
        }
        if self.resource_name in ['configmap']:
            log_config['datas'] = {
                log_key: {
                    "type": "file",
                    "content": json.dumps(log_content)
                }
            }
        else:
            log_config['data'] = {
                log_key: json.dumps(log_content)
            }
        # 实例化时，启动非标准日志采集任务
        if not self.is_preview:
            username = self.params.get('username')
            project_id = self.params.get('project_id')
            create_and_start_non_standard_data_flow(username, project_id, cc_app_id)
        return log_config

    def handle_k8s_ingress_srt(self, cert_id, ingress_id, ingress_type, cert_type):
        ingress = MODULE_DICT.get(ingress_type).objects.get(id=ingress_id)
        ingress_name = ingress.name

        project_code = self.context['SYS_PROJECT_CODE']
        self.resource_show_name = get_secret_name_by_certid(cert_id, ingress_name)
        if cert_type == 'bcstls':
            try:
                tls_cert = TlsCert.objects.get(id=cert_id)
                crt_content = tls_cert.cert
                key_content = tls_cert.key
            except Exception:
                raise ValidationError('Ingress{ingress_name}{prefix_msg} TLS {cert}(id:{cert_id}){suffix_msg}'.format(
                    ingress_name=ingress_name,
                    prefix_msg=_("中使用的"),
                    cert=_("证书"),
                    cert_id=cert_id,
                    suffix_msg=_("不存在")
                ))
        else:
            try:
                client = TicketClient(self.project_id, project_code)
                crt_content = client.get_tls_crt_content(cert_id)
                key_content = client.get_tls_key_content(cert_id)
            except Exception as e:
                message = 'Ingress{ingress_name}{prefix_msg} TLS {cert}(id:{cert_id}){suffix_msg}:{e}'.format(
                    ingress_name=ingress_name,
                    prefix_msg=_("中使用的"),
                    cert=_("证书"),
                    cert_id=cert_id,
                    suffix_msg=_("异常"),
                    e=e
                )
                raise ValidationError(message)

        srt_config = {
            "data": {
                "tls.crt": crt_content,
                "tls.key": key_content
            },
            "kind": "Secret",
            "metadata": {
                "name": self.resource_show_name
            },
            "type": "kubernetes.io/tls"
        }
        return srt_config

    def get_metric_lables(self, db_config):
        """应用中需要写入关联metric的信息
        metric 才能通过selector 关联到应用
        """
        web_cache = db_config.get('webCache') or {}
        is_metric = web_cache.get('isMetric') or False
        metric_id_list = web_cache.get('metricIdList') or []

        metric_lables = {}
        if is_metric and metric_id_list:
            metric_list = Metric.objects.filter(
                id__in=metric_id_list, is_deleted=False)
            metric_name_list = metric_list.values_list('name', flat=True)
            for _m_name in metric_name_list:
                _m_key = '%s.%s' % (LABLE_METRIC_SELECTOR_LABEL, _m_name)
                metric_lables[_m_key] = _m_name
        return metric_lables

    def inject_labels_for_monitor(self, labels, resource_kind, name):
        # labels
        labels["io.tencent.bcs.controller.type"] = resource_kind
        labels["io.tencent.bcs.controller.name"] = name

    def inject_annotations_for_monitor(self, annotations, resource_kind, name):
        annotations["io.tencent.bcs.controller.type"] = resource_kind
        annotations["io.tencent.bcs.controller.name"] = name


def handle_k8s_api_version(config_profile, cluster_id, cluster_version, controller_type):
    # 由功能开关控制是否在配置文件中添加 apiVersion 字段

    enabled, wlist = get_func_controller('IS_ADD_APIVERSION')
    if enabled or (cluster_id in wlist):
        # apiVersion 根据k8s版本自动匹配
        if cluster_version:
            # 获取资源在 k8s 配置文件中的 kind
            api_version = API_VERSION.get(cluster_version, {}).get(controller_type)
            if api_version:
                config_profile['apiVersion'] = api_version
    return config_profile


class K8sProfileGenerator(ProfileGenerator):
    """k8s 配置文件，将 json 格式转换为 yaml 格式
    """

    def __init__(self, resource_id, namespace_id, is_validate=True, **params):
        super().__init__(resource_id, namespace_id, is_validate, **params)

        global k8s_res_mapping
        from backend.apps.instance.resources import BCSResource
        for res in BCSResource:
            if K8S_MODULE_NAME not in res.__module__:
                continue

            name = str(res.__name__).lower()
            component = name + 's'  # make plural
            if component in k8s_res_mapping:
                continue

            k8s_res_mapping[component] = ''
            k8s_res_mapping[component] = res()
            k8s_res_mapping[name] = component

    def __getattr__(self, name):
        global k8s_res_mapping
        if name in k8s_res_mapping:
            component = k8s_res_mapping[name]
            if type(component) is not str:
                return component

            return k8s_res_mapping[component]

        return object.__getattribute__(self, name)

    def format_config_profile(self, config_profile):
        config_profile = json.loads(config_profile)
        remove_key(config_profile, 'apiVersion')

        cluster_id = self.context['SYS_CLUSTER_ID']
        controller_type = self.get_controller_type()
        config_profile = handle_k8s_api_version(config_profile, cluster_id, self.cluster_version, controller_type)

        return json.dumps(config_profile)

    def get_controller_type(self):
        return CATE_SHOW_NAME.get(self.resource_name, self.resource_name)


class MesosProfileGenerator(ProfileGenerator):
    def __init__(self, resource_id, namespace_id, is_validate=True, **params):
        super().__init__(resource_id, namespace_id, is_validate, **params)

        global mesos_res_mapping
        from backend.apps.instance.resources import BCSResource
        for res in BCSResource:
            if MESOS_MODULE_NAME not in res.__module__:
                continue

            name = str(res.__name__).lower()
            component = name + 's'  # make plural
            if component in mesos_res_mapping:
                continue

            mesos_res_mapping[component] = ''
            mesos_res_mapping[component] = res()
            mesos_res_mapping[name] = component

    def __getattr__(self, name):
        global mesos_res_mapping
        if name in mesos_res_mapping:
            component = mesos_res_mapping[name]
            if type(component) is not str:
                return component

            return mesos_res_mapping[component]

        return object.__getattribute__(self, name)


class ApplicationProfileGenerator(MesosProfileGenerator):
    resource_name = "application"
    resource_sys_config = APPLICATION_SYS_CONFIG

    def check_image_secret(self):
        """是否使用secret中账号信息
        1. cluster_id 是否在开启的白名单中
        2. 命名空间的 has_image_secret 为 True
        """
        cluster_id = self.context['SYS_CLUSTER_ID']
        enabled, wlist = get_func_controller('HAS_IMAGE_SECRET')
        if not enabled and (cluster_id not in wlist):
            return False
        return self.has_image_secret

    def handle_db_config(self, db_config):
        """添加选取到与关联的Application 的label
        """
        # 删除前端多余的字段
        # 0. 处理自定义网络模式
        db_config = handel_custom_network_mode(db_config)
        # 1.1 处理调度约束
        intersection_item = db_config.get(
            'constraint', {}).get("intersectionItem", [])
        new_intersection_item = handle_intersection_item(intersection_item)
        db_config['constraint']['intersectionItem'] = new_intersection_item
        # 1.3 kill 策略
        kill_p = db_config['killPolicy']
        kill_p['gracePeriod'] = handle_number_var(
            kill_p['gracePeriod'], "Application[%s]gracePeriod" % self.resource_show_name,
            self.is_preview, self.is_validate)
        # 1.4 Restart
        re_p = db_config['restartPolicy']
        re_p['interval'] = handle_number_var(
            re_p['interval'], "Application[%s]interval" % self.resource_show_name, self.is_preview, self.is_validate)
        re_p['backoff'] = handle_number_var(
            re_p['backoff'], "Application[%s]backoff" % self.resource_show_name, self.is_preview, self.is_validate)
        re_p['maxtimes'] = handle_number_var(
            re_p['maxtimes'], "Application[%s]maxtimes" % self.resource_show_name, self.is_preview, self.is_validate)
        # 1.5 实例数
        db_config['spec']['instance'] = handle_number_var(
            db_config['spec']['instance'], "Application[%s]instance" % self.resource_show_name,
            self.is_preview, self.is_validate)

        # 2. 处理 containers 中的字段
        is_custom_log_path = False
        containers = db_config.get('spec', {}).get(
            'template', {}).get('spec', {}).get('containers', [])
        jfrog_domain = self.context['SYS_JFROG_DOMAIN']
        for _c in containers:
            # 命令参数解析
            args_text = _c.get('args_text', '')
            args_list = shlex.split(args_text)
            _c['args'] = args_list

            remove_key(_c, "desc")
            remove_key(_c, "args_text")
            remove_key(_c, "parameter_list")
            remove_key(_c, "imageName")
            remove_key(_c, "imageVersion")
            # 是否添加账号信息
            if self.check_image_secret():
                _c['imagePullUser'] = 'secret::%s||user' % MESOS_IMAGE_SECRET
                _c['imagePullPasswd'] = 'secret::%s||pwd' % MESOS_IMAGE_SECRET
            # 2.0 处理镜像地址, 测试环境不处理
            if (settings.DEPOT_STAG == 'prod') and jfrog_domain:
                image = _c.get('image')
                _image_url = '//%s' % image
                _image_pares = urlparse(_image_url)
                _image_path = _image_pares.path
                _c['image'] = '%s%s' % (jfrog_domain, _image_path)

            # 2.1 处理 ports 中的字段
            ports = _c.get('ports')
            for _p in ports:
                if not all([_p.get("name"), _p.get('containerPort'), _p.get('protocol')]):
                    ports.remove(_p)
                else:
                    # TODO NUM
                    # _p['containerPort'] = int(_p.get('containerPort'))
                    # _p['hostPort'] = int(_p.get('hostPort'))
                    _p['containerPort'] = handle_number_var(
                        _p['containerPort'], "Application[%s]containerPort" % self.resource_show_name,
                        self.is_preview, self.is_validate)
                    _p['hostPort'] = handle_number_var(
                        _p['hostPort'], "Application[%s]hostPort" % self.resource_show_name,
                        self.is_preview, self.is_validate)
                    remove_key(_p, 'isDisabled')
                    remove_key(_p, 'isLink')

            # 2.2 处理 healthChecks 中的字段
            self.pod.set_health_checks(_c.get('healthChecks'), self.resource_show_name, self.is_preview,
                                       self.is_validate)

            # 2.3 处理 resources 资源限制
            self.pod.set_resources(_c.get('resources', {}))

            # 2.4 处理 volumes 中的字段
            volumes = _c.get('volumes')
            config_map_dict = {}
            sercret_dict = {}
            handle_volumes(_c['name'], volumes, db_config.get('webCache', {}).get('volumeUsers', {}), config_map_dict,
                           sercret_dict, self.template_id)

            # 2.5 处理 环境变量
            env_list = _c.get('env_list')
            env = []
            handel_env(env_list, env, config_map_dict,
                       sercret_dict, self.template_id)
            _c['env'] = env
            remove_key(_c, "env_list")

            # 2.6 添加 secrets & configmaps
            sercret_list = []
            for _sercret in sercret_dict:
                sercret_list.append({
                    'secretName': _sercret,
                    'items': sercret_dict[_sercret]
                })
            _c['secrets'] = sercret_list

            configmap_list = []
            for _conf in config_map_dict:
                configmap_list.append({
                    'name': _conf,
                    'items': config_map_dict[_conf]
                })
            _c['configmaps'] = configmap_list

            # 2.7 定义了非标准日志采集，则需要添加额外的挂载卷
            log_path_list = _c.get('logPathList') or []
            remove_key(_c, 'logListCache')
            if log_path_list:
                is_custom_log_path = True

                _c_name = _c.get('name')
                _config_name = '%s-%s-%s' % (self.resource_show_name,
                                             _c_name, LOG_CONFIG_MAP_SUFFIX)
                _config_data_key = '%s%s' % (
                    self.resource_show_name, LOG_CONFIG_MAP_KEY_SUFFIX)
                log_config_map = {
                    "name": _config_name,
                    "items": [
                        {
                            "type": "file",
                            "dataKey": _config_data_key,
                            "dataKeyAlias": _config_data_key,
                            "KeyOrPath": "%s%s" % (LOG_CONFIG_MAP_PATH_PRFIX, _config_data_key),
                            "readOnly": False,
                            "user": "root"
                        }
                    ]
                }
                _c['configmaps'].append(log_config_map)

        # 1.2. Application 打上标识的label
        labels = db_config['metadata']['labels']
        app_label_key = '%s.%s' % (LABEL_SERVICE_NAME, self.resource_show_name)
        labels[app_label_key] = self.resource_show_name
        if is_custom_log_path:
            labels[LOG_CONFIG_MAP_APP_LABEL] = '%s%s%s' % (
                LOG_CONFIG_MAP_PATH_PRFIX, self.resource_show_name, LOG_CONFIG_MAP_KEY_SUFFIX)

        # 1.2.1 打上关联metric的label
        metric_lables = self.get_metric_lables(db_config)
        if metric_lables:
            labels.update(metric_lables)

        # 1.3 添加监控的标签
        self.inject_labels_for_monitor(
            labels, self.resource_name, self.resource_show_name
        )
        self.inject_annotations_for_monitor(
            db_config["metadata"]["annotations"], self.resource_name, self.resource_show_name)

        # 1.4 添加监控需要的重要级别
        labels[LABEL_MONITOR_LEVEL] = db_config.get('monitorLevel', LABEL_MONITOR_LEVEL_DEFAULT)
        remove_key(db_config, 'monitorLevel')

        # 1.5 附加日志标签
        custom_log_label = db_config.get('customLogLabel')
        if not isinstance(custom_log_label, dict):
            custom_log_label = {}
        custom_log_label = json.dumps(custom_log_label)
        labels[MESOS_CUSTOM_LOG_LABEL_KEY] = custom_log_label
        remove_key(db_config, 'customLogLabel')
        return db_config


class DeploymentProfileGenerator(ProfileGenerator):
    resource_name = "deployment"
    resource_sys_config = DEPLPYMENT_SYS_CONFIG

    def get_resource_config(self):
        deployment_extra_config = copy.deepcopy(self.resource_sys_config)
        db_config = self.get_db_config()
        deployment_extra_config['spec']['strategy'] = db_config.get('strategy')

        # 处理数字类型的参数
        rolling = deployment_extra_config['spec']['strategy']['rollingupdate']
        rolling['maxUnavilable'] = handle_number_var(
            rolling['maxUnavilable'], "Deployment[%s]maxUnavilable" %
                                      self.resource_show_name, self.is_preview, self.is_validate)
        rolling['maxSurge'] = handle_number_var(
            rolling['maxSurge'], "Deployment[%s]maxSurge" %
                                 self.resource_show_name, self.is_preview, self.is_validate)
        rolling['upgradeDuration'] = handle_number_var(
            rolling['upgradeDuration'], "Deployment[%s]upgradeDuration" %
                                        self.resource_show_name, self.is_preview, self.is_validate)

        # 查询 Deployment 关联的 Application
        version_id = self.params.get('version_id')
        deployment_app = VersionedEntity.get_application_by_deployment_id(
            version_id, self.resource_id)
        app_config = ApplicationProfileGenerator(
            deployment_app.id,
            self.namespace_id,
            **self.params).get_resource_config()

        new_config = update_nested_dict(app_config, deployment_extra_config)
        # 将名称修改为模板中 Deployment 的名称
        new_config['metadata']['name'] = self.resource_show_name
        # 添加监控的标签
        self.inject_labels_for_monitor(
            new_config['metadata']['labels'], self.resource_name, self.resource_show_name)
        self.inject_annotations_for_monitor(
            new_config["metadata"]["annotations"], self.resource_name, self.resource_show_name)

        return new_config


class ServiceProfileGenerator(ProfileGenerator):
    resource_name = "service"
    resource_sys_config = SEVICE_SYS_CONFIG

    def handle_db_config(self, db_config):
        """添加选取到与关联的Application 的约束条件
        """
        # service 关联的 App，添加 selector 信息
        service_app_list = VersionedEntity.get_related_apps_by_service(
            self.version_id, self.resource_id)
        app_weight = self.resource.get_app_weight()
        service_name = db_config.get('metadata', {}).get('name')
        lb_name = self.lb_info.get(self.namespace_id, {}).get(
            service_name) or 'external'
        db_config = handel_service_db_config(
            db_config, service_app_list, app_weight, lb_name, self.version_id, self.is_preview, self.is_validate)
        # 注入monitor需要信息
        self.inject_labels_for_monitor(
            db_config["metadata"]["labels"], self.resource_name, self.resource_show_name)
        self.inject_annotations_for_monitor(
            db_config["metadata"]["annotations"], self.resource_name, self.resource_show_name)

        return db_config


class ConfigMapProfileGenerator(ProfileGenerator):
    resource_name = "configmap"
    resource_sys_config = CONFIGMAP_SYS_CONFIG

    def handle_db_config(self, db_config):
        """文件类型时，需要 base64
        """
        datas = db_config['datas']
        for _key in datas:
            _type = datas[_key].get('type')
            if _type == 'file':
                _c = datas[_key]['content']
                datas[_key]['content'] = base64.b64encode(
                    _c.encode(encoding="utf-8")).decode()
        return db_config


class SecretProfileGenerator(ProfileGenerator):
    resource_name = "secret"
    resource_sys_config = SECRET_SYS_CONFIG

    def handle_db_config(self, db_config):
        """数据内容需要 base64
        """
        datas = db_config['datas']
        for _key in datas:
            _c = datas[_key]['content']
            datas[_key]['content'] = base64.b64encode(
                _c.encode(encoding="utf-8")).decode()
        return db_config


class HPAProfileGenerator(ProfileGenerator):
    resource_name = "hpa"
    resource_sys_config = instance_constants.HPA_SYS_CONFIG


class IngressProfileGenerator(ProfileGenerator):
    resource_name = 'ingress'
    resource_sys_config = instance_constants.INGRESS_SYS_CONFIG

    def handle_db_config(self, db_config):
        """针对ingress下的service配置添加namespace
        """
        spec = db_config['spec']
        for protocol in spec:
            for info in spec[protocol]:
                info['namespace'] = self.context['SYS_NAMESPACE']
        db_config['spec'] = spec
        return db_config


class MetricProfileGenerator(ProfileGenerator):
    resource_name = "metric"
    resource_sys_config = {}

    def handle_db_config(self, application_id, metric_id, resourse_type='application'):
        """组装 metric 的配置文件
        """
        try:
            met = Metric.objects.get(id=metric_id)
        except Exception:
            raise ValidationError('Metric[id:{}]:{}'.format(metric_id, _("不存在")))
        self.resource_show_name = met.name
        api_json = met.to_api_json()
        api_json['namespace'] = self.context['SYS_NAMESPACE']
        api_json['clusterID'] = self.context['SYS_CLUSTER_ID']
        # 添加集群对应的仓库域名
        api_json['imageBase'] = self.context['SYS_JFROG_DOMAIN']
        # 添加k8s的账号信息
        api_json['imagePullSecrets'] = [
            {'name': "%s%s" % (K8S_IMAGE_SECRET_PRFIX,
                               self.context['SYS_NAMESPACE'])}
        ]

        try:
            application = MODULE_DICT.get(
                resourse_type).objects.get(id=application_id)
        except Exception:
            raise ValidationError('{}[id:{}]:{}'.format(_("应用"), application_id, _("不存在")))
        if resourse_type == 'application':
            app_config = application.get_config()
            app_config_new = handel_custom_network_mode(app_config)
            app_spec = app_config_new.get('spec', {}).get(
                'template', {}).get('spec', {})
            api_json['networkMode'] = app_spec.get('networkMode')
            api_json['networkType'] = app_spec.get('networkType')
        else:
            pod_config = application.get_config()
            pod_spec = pod_config.get('spec', {}).get(
                'template', {}).get('spec', {})
            # 1.1. hostNetwork 0/1 转换为 false/true
            host_network = pod_spec.get('hostNetwork')
            dns_policy = pod_spec.get('dnsPolicy')
            host_network = True if host_network else False
            api_json['dnsPolicy'] = dns_policy
            api_json['hostNetwork'] = host_network
            # k8s 相关的资源网络信息用默认值
            api_json['networkMode'] = "BRIDGE"
            api_json['networkType'] = "cnm"
        # 获取metric的唯一标识
        metric_label_key = '%s.%s' % (
            LABLE_METRIC_SELECTOR_LABEL, self.resource_show_name)

        api_json['selector'] = {
            metric_label_key: self.resource_show_name
        }
        return api_json


def handel_custom_network_mode(db_config):
    """处理自定义网络模式
    """
    spec = db_config.get('spec', {}).get('template', {}).get('spec', {})
    network_mode = spec.get('networkMode')
    if network_mode == 'CUSTOM':
        spec['networkMode'] = spec.get('custom_value')
    remove_key(spec, 'custom_value')
    return db_config


def handle_intersection_item(intersection_item):
    """处理前端的存储的调度约束
    """
    new_intersection_item = []
    for _intersection in intersection_item:
        union_data = _intersection.get("unionData")[0]

        # InnerIP 替换
        name = union_data.get('name')
        if name == "InnerIp":
            union_data['name'] = "InnerIP"

        # operate = union_data.get('operate')
        arg_value = union_data.get('arg_value')

        _type = union_data.get('type')
        if _type not in [3, 4] or arg_value:
            remove_key(union_data, "arg_value")
            new_intersection_item.append({"unionData": [union_data]})
    return new_intersection_item


def handle_volumes(container_name, volumes, volume_users, config_map_dict, sercret_dict, template_id):
    for _v in range(len(volumes) - 1, -1, -1):
        _v_value = volumes[_v]
        _name = _v_value.get('name')
        # 处理前端传过来的空数据
        if not _name:
            volumes.pop(_v)
            continue
        # 挂载源
        host_path = _v_value.get('volume').get('hostPath')
        # 容器目录
        mount_path = _v_value.get('volume').get('mountPath')
        # 处理不同类型的挂在卷
        _type = _v_value.get('type')
        # 挂载源: name.data_key
        _prefix_len = len(_name) + 1
        _data_key = host_path[_prefix_len:]

        # 实例化后的名称与模板集中的名称保持一致
        _real_name = _name
        if _type == 'configmap':
            _item_list = config_map_dict.get(_real_name, [])
            _item_list.append({
                'type': 'file',
                'readOnly': False,
                'user': volume_users.get(container_name, {}).get(f"{_type}:{_real_name}:{_data_key}:{mount_path}", ''),
                'dataKey': _data_key,
                'dataKeyAlias': _data_key,
                'KeyOrPath': mount_path,
            })
            config_map_dict[_real_name] = _item_list
            volumes.pop(_v)
        elif _type == 'secret':
            _item_list = sercret_dict.get(_real_name, [])
            _item_list.append({
                'type': 'file',
                'readOnly': False,
                'user': volume_users.get(container_name, {}).get(f"{_type}:{_real_name}:{_data_key}:{mount_path}", ''),
                'dataKey': _data_key,
                'KeyOrPath': mount_path,
            })
            sercret_dict[_real_name] = _item_list
            volumes.pop(_v)
        else:
            # 自定义情况下，把前端加上的 type 字段去掉
            remove_key(_v_value, 'type')


def handel_env(env_list, env, config_map_dict, sercret_dict, template_id):
    """处理前端的环境变量：自定义&configmap&secret
    """
    for _env in env_list:
        _type = _env.get('type')
        _key = _env.get('key')
        _value = _env.get('value')
        if not all([_type, _key, _value]):
            continue
        if _type == 'custom':
            env.append({
                "name": _key,
                "value": _value
            })
        else:
            _name = _value.split('.')[0]
            _prefix_len = len(_name) + 1
            _data_key = _value[_prefix_len:]

            # 实例化后的名称与模板中的名称保持一致
            _real_name = _name
            if _type == 'configmap':
                _item_list = config_map_dict.get(_real_name, [])
                _item_list.append({
                    'type': 'env',
                    'dataKey': _data_key,
                    'KeyOrPath': _key,
                })
                config_map_dict[_real_name] = _item_list
            else:
                _item_list = sercret_dict.get(_real_name, [])
                _item_list.append({
                    'type': 'env',
                    'dataKey': _data_key,
                    'KeyOrPath': _key,
                })
                sercret_dict[_real_name] = _item_list


def handel_service_db_config(db_config, service_app_list, app_weight, lb_name, version_id,
                             is_preview=False, is_validate=True):
    """处理service的配置数据
    """
    # service 关联的 App，添加 selector 信息
    if service_app_list:
        selector = {}
        # 给关联的应用设置权重
        for _app in service_app_list:
            app_key = '%s.%s' % (LABEL_SERVICE_NAME, _app.name)
            selector[app_key] = _app.name
            _weight = app_weight.get(_app.app_id)
            _weight_key = '%s%s' % (
                SEVICE_WEIGHT_LABEL_PREFIX, _app.name)
            db_config['metadata']['labels'][_weight_key] = str(_weight)
        db_config['spec']['selector'] = selector

    # 删除前端多余的字段
    is_link_lb = db_config.get('isLinkLoadBalance')
    # 1. 处理负载均衡算法
    if is_link_lb:
        lb_algorithm = db_config.get('metadata', {}).get(
            'lb_labels', {}).get('BCSBALANCE')
        db_config['metadata']['labels']['BCSBALANCE'] = lb_algorithm or 'roundrobin'
        # 删除多余的 label
        remove_key(db_config['metadata'], 'lb_labels')
        # 1.1 添加绑定的 lb name 到 label 中
        # bcs - loadbalance模块的集群ID，默认值external
        db_config['metadata']['labels']['BCSGROUP'] = lb_name
    remove_key(db_config, 'isLinkLoadBalance')

    # 2.type 为 None 时，删除 clusterIP 项
    _type = db_config['spec']['type']
    if _type == 'None':
        remove_key(db_config['spec'], 'clusterIP')

    # 3.port 为整数
    ports = db_config['spec']['ports']

    app_id_list = service_app_list.values_list('app_id', flat=True)
    version = VersionedEntity.objects.get(id=version_id)
    app_ports = version.get_version_ports(app_id_list)
    ports_dict = {i['id']: {'name': i['name'], 'protocol': i['protocol']} for i in app_ports}

    for _p in ports:
        if not all([_p.get("name"), _p.get('servicePort'), _p.get('protocol')]):
            ports.remove(_p)
        else:
            _p['servicePort'] = handle_number_var(
                _p['servicePort'], f"Service[{db_config['metadata']['name']}]service port", is_preview, is_validate)
            remove_key(_p, "targetPort")
            # 端口名称 和 协议 根据 id 从 Application 中获取
            _id = _p.get('id')
            if _id:
                _app_ports_data = ports_dict.get(_id)
                if _app_ports_data:
                    _p['name'] = _app_ports_data['name']
                    _p['protocol'] = _app_ports_data['protocol']
    # 前端缓存数据存储到 annocation 中
    web_cache = db_config.get('webCache', {})
    if web_cache:
        if 'annotations' in db_config['metadata']:
            db_config['metadata']['annotations'][ANNOTATIONS_WEB_CACHE] = json.dumps(
                web_cache)
        else:
            db_config['metadata']['annotations'] = {
                ANNOTATIONS_WEB_CACHE: json.dumps(web_cache)
            }
    return db_config


def handle_webcache_config(resource_config):
    """将前端的缓存的数据存储到备注中
    """
    web_cache = resource_config.get('webCache', {})
    if web_cache and ('metadata' in resource_config):
        if 'annotations' in resource_config['metadata']:
            resource_config['metadata']['annotations'][ANNOTATIONS_WEB_CACHE] = json.dumps(
                web_cache)
        else:
            resource_config['metadata']['annotations'] = {
                ANNOTATIONS_WEB_CACHE: json.dumps(web_cache)
            }
    # 删除前端缓存中间信息的key
    remove_key(resource_config, 'webCache')
    return resource_config


def get_bcs_context(access_token, project_id):
    # 获取项目相关的信息
    context = {}
    project = paas_cc.get_project(access_token, project_id)
    if project.get('code') != 0:
        raise ValidationError('{}(project_id:{}):{}'.format(_("查询项目信息出错"), project_id, project.get('message')))
    project = project.get('data') or {}
    context['SYS_CC_APP_ID'] = project.get('cc_app_id')
    # TODO  以下变量未初始化到变量表中
    context['SYS_PROJECT_KIND'] = ClusterType.get(project.get('kind'), '')
    context['SYS_PROJECT_CODE'] = project.get('english_name')

    # 获取标准日志采集的dataid
    data_info = get_data_id_by_project_id(project_id)
    context['SYS_STANDARD_DATA_ID'] = data_info.get('standard_data_id')
    context['SYS_NON_STANDARD_DATA_ID'] = data_info.get('non_standard_data_id')
    return context


def remove_key(d, key):
    if key in d:
        del d[key]
    return d


# ############################## k8s 相关资源

class K8sSecretGenerator(K8sProfileGenerator):
    resource_name = "K8sSecret"
    resource_sys_config = K8S_SECRET_SYS_CONFIG

    def handle_db_config(self, db_config):
        """type: 默认Opaque, 需要 base64
        """
        datas = db_config['data']
        for _key in datas:
            _c = datas[_key]
            datas[_key] = base64.b64encode(
                _c.encode(encoding="utf-8")).decode()
        return db_config


class K8sConfigMapGenerator(K8sProfileGenerator):
    resource_name = "K8sConfigMap"
    resource_sys_config = K8S_CONFIGMAP_SYS_CONFIG

    def handle_db_config(self, db_config):
        """
        """
        return db_config


class K8sIngressGenerator(K8sProfileGenerator):
    resource_name = "K8sIngress"
    resource_sys_config = K8S_INGRESS_SYS_CONFIG

    def handle_db_config(self, db_config):
        """
        """
        # 根据证书获取secretName
        tls_list = db_config.get('spec', {}).get('tls', [])
        for _tls in tls_list:
            cert_id = _tls.get('certId')
            if cert_id:
                secret_name = get_secret_name_by_certid(cert_id, self.resource_show_name)
                _tls['secretName'] = secret_name
            remove_key(_tls, 'certId')
            remove_key(_tls, 'certType')

            # 移除 host 里面为空的项目（前端的占位符)
            if 'hosts' in _tls:
                _tls_host = _tls['hosts']
                _tls['hosts'] = [_h for _h in _tls_host if _h]

        # 去掉路径组中为空的项（前端的占位符）
        rules_list = db_config.get('spec', {}).get('rules', [])
        for rules in rules_list:
            r_http = rules.get('http') or {}
            r_paths = r_http.get('paths') or []
            real_path = []
            for _p in r_paths:
                _p_backend = _p.get('backend') or {}
                if any([_p.get('path'), _p_backend.get('serviceName'), _p_backend.get('servicePort')]):
                    real_path.append(_p)
            if real_path:
                r_http['paths'] = real_path
            else:
                remove_key(r_http, 'paths')
            if not rules.get('http'):
                remove_key(rules, 'http')
        return db_config


class K8sServiceGenerator(K8sProfileGenerator):
    resource_name = "K8sService"
    resource_sys_config = K8S_SEVICE_SYS_CONFIG

    def handle_db_config(self, db_config):
        """添加选取到与关联的Application 的约束条件
        """
        deploy_tag_list = self.resource.get_deploy_tag_list()
        db_config = handel_k8s_service_db_config(
            db_config, deploy_tag_list, self.version_id, is_preview=self.is_preview, is_validate=self.is_validate)
        self.inject_labels_for_monitor(
            db_config["metadata"]["labels"], self.get_controller_type(), self.resource_show_name)
        self.inject_annotations_for_monitor(
            db_config["metadata"]["annotations"], self.get_controller_type(), self.resource_show_name)
        return db_config


def handel_k8s_service_db_config(db_config, deploy_tag_list, version_id,
                                 is_upadte=False, is_preview=False, is_validate=True, variable_dict={}):
    """  Service 操作单独处理，方便单独更新Service操作
    """
    # selector 信息，为空，则不生成该key
    if not db_config.get('spec', {}).get('selector'):
        remove_key(db_config['spec'], 'selector')
    # 端口信息二次处理
    s_type = db_config.get('spec', {}).get('type', '')
    ports = db_config.get('spec', {}).get('ports', [])

    if not db_config.get('spec', {}).get('clusterIP', ''):
        remove_key(db_config['spec'], 'clusterIP')
    elif s_type == 'NodePort' and not is_upadte:
        remove_key(db_config['spec'], 'clusterIP')
    # Service 关联的端口应用的端口信
    # 获取所有端口中的id
    ports_dict = {}
    if ports:
        ventity = VersionedEntity.objects.get(id=version_id)
        pod_qsets = get_pod_qsets_by_tag(deploy_tag_list, ventity)
        pod_ports = get_k8s_container_ports(pod_qsets)
        ports_dict = {i['id']: i['name'] for i in pod_ports}
    for _p in ports:
        # 端口 & 协议必填
        if not all([_p.get('port'), _p.get('protocol')]):
            ports.remove(_p)
        else:
            # 目标端口根据id从关联的模板集资源中获取 targetPort
            prot_id = _p.get('id')
            port_name = ports_dict.get(prot_id)
            # 替换模板名称中变量
            port_name = render_mako_context(port_name, variable_dict)
            if prot_id and port_name:
                _p['targetPort'] = port_name
                remove_key(_p, 'id')
            # targetPort 为 "234" 时需要转成数字: 234
            try:
                _p['targetPort'] = int(_p['targetPort'])
            except Exception:
                pass
            # 只有 Service 类型为 NodePort 时才传 nodePort 字段
            if s_type != 'NodePort':
                remove_key(_p, "nodePort")
            else:
                if not _p['nodePort']:
                    remove_key(_p, "nodePort")
                else:
                    _p['nodePort'] = handle_number_var(
                        _p['nodePort'], "Service[%s]nodePort" % db_config['metadata']['name'], is_preview, is_validate)
            _p['port'] = handle_number_var(
                _p['port'], "Service[%s]port" % db_config['metadata']['name'], is_preview, is_validate)
    if not ports:
        remove_key(db_config['spec'], 'ports')
    return db_config


class K8sDeploymentGenerator(K8sProfileGenerator):
    resource_name = "K8sDeployment"
    resource_sys_config = K8S_DEPLPYMENT_SYS_CONFIG

    def handle_pod_config(self, db_config):
        db_spec = db_config['spec']
        self.pod.set_base_spec(
            db_spec, self.resource_name, self.resource_show_name, self.is_preview, self.is_validate
        )
        self.pod.set_strategy(
            db_spec['strategy'], self.resource_name, self.resource_show_name, self.is_preview, self.is_validate
        )
        return db_config

    def handle_db_config(self, db_config):
        """
        """
        db_config = self.handle_pod_config(db_config)

        # 0.选择器为空则删除key
        if 'selector' in db_config.get('spec'):
            db_selector = db_config['spec']['selector']
            match_labels = db_selector.get('matchLabels')
            if not match_labels:
                remove_key(db_selector, 'matchLabels')
            if not db_selector:
                remove_key(db_config['spec'], 'selector')

        # 0.1 实例数
        if 'replicas' in db_config['spec']:
            db_config['spec']['replicas'] = handle_number_var(
                db_config['spec']['replicas'], "%s[%s]replicas" %
                                               (self.resource_name, self.resource_show_name),
                self.is_preview, self.is_validate)

        pod_tem = db_config.get('spec', {}).get(
            'template', {})
        pod_spec = pod_tem.get('spec', {})
        # 1.1. hostNetwork 0/1 转换为 false/true
        host_network = pod_spec.get('hostNetwork')
        pod_spec['hostNetwork'] = True if host_network else False

        # 1.2 有container的资源都需要打一个唯一的label,以便其他资源 selector
        app_label_key = '%s.%s.%s' % (
            LABLE_CONTAINER_SELECTOR_LABEL, self.resource_name, self.resource_show_name)
        if 'labels' in db_config['metadata']:
            db_config['metadata']['labels'][app_label_key] = self.resource_show_name
        else:
            db_config['metadata']['labels'] = {
                app_label_key: self.resource_show_name
            }

        pod_lables = db_config['spec']['template']['metadata']['labels']
        pod_lables[app_label_key] = self.resource_show_name

        # 1.2.1 pod label 中添加重要级别
        pod_lables[LABEL_MONITOR_LEVEL] = db_config.get('monitorLevel', LABEL_MONITOR_LEVEL_DEFAULT)
        remove_key(db_config, 'monitorLevel')

        # 1.2.2 添加监控相关
        self.inject_labels_for_monitor(pod_lables, self.get_controller_type(), self.resource_show_name)

        # 添加关联的metric的label
        metric_lables = self.get_metric_lables(db_config)
        if metric_lables:
            db_config['metadata']['labels'].update(metric_lables)
            pod_lables.update(metric_lables)

        # 1.3 处理空数据
        if not pod_spec.get('nodeSelector'):
            remove_key(pod_spec, 'nodeSelector')
        if not pod_spec.get('affinity'):
            remove_key(pod_spec, 'affinity')
        if not pod_spec.get('volumes'):
            remove_key(pod_spec, 'volumes')
        if not pod_tem.get('metadata', {}).get('annotations', {}):
            remove_key(pod_tem['metadata'], 'annotations')

        # 1.3 添加镜像的账号的 Secret
        pod_spec['imagePullSecrets'] = [
            {'name': "%s%s" % (K8S_IMAGE_SECRET_PRFIX,
                               self.context['SYS_NAMESPACE'])}
        ]

        # 1.4 处理数字类型
        pod_spec['terminationGracePeriodSeconds'] = handle_number_var(
            pod_spec['terminationGracePeriodSeconds'], "%s[%s]terminationGracePeriodSeconds" %
                                                       (self.resource_name, self.resource_show_name),
            self.is_preview, self.is_validate)

        # 1.5 附加日志标签
        custom_log_label = db_config.get('customLogLabel')
        if not isinstance(custom_log_label, dict):
            custom_log_label = {}
        custom_log_label = json.dumps(custom_log_label)
        remove_key(db_config, 'customLogLabel')

        # 2. 处理container 中的数据
        # is_custom_log_path = False
        containers = db_config.get('spec', {}).get(
            'template', {}).get('spec', {}).get('containers', [])
        init_containers = db_config.get('spec', {}).get(
            'template', {}).get('spec', {}).get('initContainers', [])

        jfrog_domain = self.context['SYS_JFROG_DOMAIN']
        log_volumes = []

        for con_list in [init_containers, containers]:
            for _c in con_list:
                remove_key(_c, "imageVersion")

                # 2.0 处理镜像地址, 测试环境不处理
                if (settings.DEPOT_STAG == 'prod') and jfrog_domain:
                    image = _c.get('image')
                    _image_url = '//%s' % image
                    _image_pares = urlparse(_image_url)
                    _image_path = _image_pares.path
                    _c['image'] = '%s%s' % (jfrog_domain, _image_path)
                # 2.1 启动命令和参数用 shellhex 命令处理为数组
                args = _c.get('args')
                args_list = shlex.split(args)
                _c['args'] = args_list
                command = _c.get('command')
                command_list = shlex.split(command)
                _c['command'] = command_list

                # 2.2 lifecycle.command 用 shellhex 命令处理为数组
                lifecycle = _c['lifecycle']
                pre_stop_command = lifecycle['preStop']['exec']['command']
                pre_stop_command_list = shlex.split(pre_stop_command)
                if pre_stop_command_list:
                    lifecycle['preStop']['exec']['command'] = pre_stop_command_list
                else:
                    remove_key(lifecycle, 'preStop')

                post_start_command = lifecycle['postStart']['exec']['command']
                post_start_command_list = shlex.split(post_start_command)
                if post_start_command_list:
                    lifecycle['postStart']['exec']['command'] = post_start_command_list
                else:
                    remove_key(lifecycle, 'postStart')

                web_cache = _c.get('webCache', {})
                # 2.3 健康&就绪检查, 判断是否存在
                # 健康&就绪检查 type 存放在 curContainer.webCache.livenessProbeType/curContainer.webCache.readinessProbeType
                liveness_type = web_cache.get('livenessProbeType')
                liveness_probe = _c['livenessProbe']
                is_liveness_exit = handel_container_health_check_type(
                    liveness_probe, liveness_type, self.is_preview, self.is_validate)
                if not is_liveness_exit:
                    remove_key(_c, 'livenessProbe')

                readiness_tye = web_cache.get('readinessProbeType')
                readiness_probe = _c['readinessProbe']
                is_readiness_exit = handel_container_health_check_type(
                    readiness_probe, readiness_tye, self.is_preview, self.is_validate)
                if not is_readiness_exit:
                    remove_key(_c, 'readinessProbe')

                # 2.4 resources 资源限制后添加单位，且不填则不生成相应的key
                resources = _c['resources']
                for _key in ['limits', 'requests']:
                    handle_container_resources(resources, _key, self.is_preview)
                if not resources:
                    remove_key(_c, 'resources')

                # 2.5 环境变量后台转换
                env_list = _c.get('webCache', {}).get('env_list')
                env, env_from = handle_container_env(env_list)
                _c['env'] = env
                _c['envFrom'] = env_from
                # 环境变量中需要添加日志需要的变量
                _c['env'].extend(K8S_LOG_ENV)
                # 环境变量中需要 添加 pod controller 类型的名称
                controller_env = [
                    {"name": "io_tencent_bcs_controller_type", "value": self.get_controller_type()},
                    {"name": "io_tencent_bcs_controller_name", "value": self.resource_show_name},
                ]
                _c['env'].extend(controller_env)
                # 环境变量中需要添加附加日志标签
                _c['env'].append({
                    'name': K8S_CUSTOM_LOG_ENV_KEY,
                    'value': custom_log_label
                })

                # 2.6 处理数字类型的数据
                c_ports = _c['ports']
                for _p in c_ports:
                    _p['containerPort'] = handle_number_var(
                        _p['containerPort'], "%s[%s]containerPort" %
                                             (self.resource_name, self.resource_show_name),
                        self.is_preview, self.is_validate)
                # 2.7定义了非标准日志采集，则需要添加额外的挂载卷
                log_path_list = _c.get('logPathList') or []
                if log_path_list:
                    _c_name = _c.get('name')
                    _config_name = '%s-%s-%s' % (self.resource_show_name, _c_name, LOG_CONFIG_MAP_SUFFIX)
                    # 挂载卷名称要限制在 64 个字符内
                    _vol_name = '%s-%s' % (LOG_CONFIG_MAP_SUFFIX, uuid.uuid4().hex)
                    # 挂载的文件名
                    _mount_file_name = '%s%s' % (self.resource_show_name, LOG_CONFIG_MAP_KEY_SUFFIX)
                    # 挂载的路径
                    _mount_path = '%s%s' % (LOG_CONFIG_MAP_PATH_PRFIX, _mount_file_name)
                    log_config_map = {
                        "name": _vol_name,
                        "mountPath": _mount_path,
                        "subPath": _mount_file_name,
                        "readOnly": False
                    }
                    _c['volumeMounts'].append(log_config_map)
                    log_volumes.append({
                        "name": _vol_name,
                        "configMap": {
                            "name": _config_name
                        }
                    })
                    # 在环境变量中添加label的配置
                    _c['env'].append({
                        "name": LOG_CONFIG_MAP_APP_LABEL.replace('.', '_'),
                        "value": _mount_path
                    })

                # 2.8 空数据则不生成key
                s_key = list(_c.keys())
                for _c_key in s_key:
                    if not _c[_c_key]:
                        del _c[_c_key]
                # 2.9 删除前端缓存数据
                remove_key(_c, 'webCache')

        if log_volumes:
            if 'volumes' in pod_spec:
                pod_spec['volumes'].extend(log_volumes)
            else:
                pod_spec['volumes'] = log_volumes
        return db_config


def handle_container_env(env_list):
    """将前端的 env_list 转换为k8s的env
    """
    env = []
    env_from = []
    for _env in env_list:
        _type = _env.get('type')
        if _type == 'custom':
            if _env.get('key'):
                env.append({
                    'name': _env['key'],
                    'value': _env.get('value')
                })
        elif _type in ['valueForm', 'valueFrom']:
            if _env.get('key'):
                env.append({
                    'name': _env['key'],
                    'valueFrom': {
                        'fieldRef': {
                            'fieldPath': _env.get('value')
                        }
                    }
                })
        elif _type in ['configmapKey', 'secretKey']:
            if _env.get('key'):
                _value = _env.get('value')
                _name = _value.split('.')[0]
                _prefix_len = len(_name) + 1
                _data_key = _value[_prefix_len:]
                env.append({
                    'name': _env['key'],
                    'valueFrom': {
                        K8S_ENV_KEY.get(_type): {
                            'name': _name,
                            'key': _data_key
                        }
                    }
                })
        elif _type in ['configmapFile', 'secretFile']:
            if _env.get('value'):
                env_from.append({
                    K8S_ENV_KEY.get(_type): {
                        'name': _env['value']
                    }
                })
    return env, env_from


def handle_container_resources(resources, key, is_preview=False):
    """资源限制，资源限制后添加单位，且不填则不生成相应的key
    """
    for _type in ['cpu', 'memory']:
        _type_v = resources[key][_type]
        if is_preview:
            if _type_v:
                resources[key][_type] = '%s%s' % (
                    _type_v, K8S_RESOURCE_UNIT.get(_type))
            else:
                remove_key(resources[key], _type)
        else:
            try:
                _type_v = int(_type_v)
            except Exception:
                remove_key(resources[key], _type)
            else:
                resources[key][_type] = '%s%s' % (
                    _type_v, K8S_RESOURCE_UNIT.get(_type))
    if not resources[key]:
        remove_key(resources, key)


def handel_container_health_check_type(health, type, is_preview=False, is_validate=True):
    """健康检查 & 就绪检查
    """
    if 'initialDelaySeconds' in health:
        health['initialDelaySeconds'] = handle_number_var(
            health['initialDelaySeconds'], "initialDelaySeconds", is_preview, is_validate)
    if 'periodSeconds' in health:
        health['periodSeconds'] = handle_number_var(
            health['periodSeconds'], "periodSeconds", is_preview, is_validate)
    if 'timeoutSeconds' in health:
        health['timeoutSeconds'] = handle_number_var(
            health['timeoutSeconds'], "timeoutSeconds", is_preview, is_validate)
    if 'failureThreshold' in health:
        health['failureThreshold'] = handle_number_var(
            health['failureThreshold'], "failureThreshold", is_preview, is_validate)
    if 'successThreshold' in health:
        health['successThreshold'] = handle_number_var(
            health['successThreshold'], "successThreshold", is_preview, is_validate)
    if type == 'HTTP':
        remove_key(health, "tcpSocket")
        remove_key(health, "exec")
        http_port = health['httpGet']['port']
        http_path = health['httpGet']['path']

        if not all([http_port, http_path]):
            return False
        else:
            http_headers = health['httpGet']['httpHeaders']
            if not http_headers:
                remove_key(health['httpGet'], 'httpHeaders')
    elif type == 'TCP':
        remove_key(health, "httpGet")
        remove_key(health, "exec")
        tcp_port = health['tcpSocket']['port']
        if not tcp_port:
            return False
    elif type == 'EXEC':
        remove_key(health, "httpGet")
        remove_key(health, "tcpSocket")
        # exec.command 多个参数用空格分隔，组装为数组后存储
        exec_command = health['exec']['command']
        exec_command_list = shlex.split(exec_command)
        if exec_command_list:
            health['exec']['command'] = exec_command_list
        else:
            return False
    return True


class K8sDaemonSetGenerator(K8sDeploymentGenerator):
    resource_name = "K8sDaemonSet"
    resource_sys_config = K8S_DAEMONSET_SYS_CONFIG

    def handle_pod_config(self, db_config):
        # 配置文件中去掉 spec.replicas
        remove_key(db_config['spec'], 'replicas')
        return db_config


class K8sJobGenerator(K8sDeploymentGenerator):
    resource_name = "K8sJob"
    resource_sys_config = K8S_JOB_SYS_CONFIG

    def handle_pod_config(self, db_config):
        # 配置文件中去掉 spec.replicas
        db_spec = db_config['spec']
        remove_key(db_spec, 'replicas')
        # 处理数字类型数据
        db_spec['completions'] = handle_number_var(
            db_spec['completions'], "%s[%s]completions" %
                                    (self.resource_name, self.resource_show_name),
            self.is_preview, self.is_validate)
        db_spec['parallelism'] = handle_number_var(
            db_spec['parallelism'], "%s[%s]parallelism" %
                                    (self.resource_name, self.resource_show_name),
            self.is_preview, self.is_validate)
        db_spec['backoffLimit'] = handle_number_var(
            db_spec['backoffLimit'], "%s[%s]backoffLimit" %
                                     (self.resource_name, self.resource_show_name),
            self.is_preview, self.is_validate)
        return db_config


class K8sStatefulSetGenerator(K8sDeploymentGenerator):
    resource_name = "K8sStatefulSet"
    resource_sys_config = K8S_STATEFULSET_SYS_CONFIG

    def handle_pod_config(self, db_config):
        pvc_list = db_config.get('spec', {}).get('volumeClaimTemplates', [])
        for pvc_num in range(len(pvc_list) - 1, -1, -1):
            pvc = pvc_list[pvc_num]
            pvc_name = pvc.get('metadata', {}).get('name')
            pvc_class_name = pvc.get('spec', {}).get('storageClassName')
            storage = pvc.get('spec', {}).get(
                'resources', {}).get('requests', {}).get('storage')
            if all([pvc_name, pvc_class_name, storage]):
                # volumeClaimTemplates storage 添加单位 Gi
                pvc['spec']['resources']['requests']['storage'] = '%sGi' % storage
            else:
                pvc_list.pop(pvc_num)
        # 没有 pvc 数据，则不生成 volumeClaimTemplates key
        if not pvc_list:
            remove_key(db_config['spec'], 'volumeClaimTemplates')

        # 获取关联的Service
        service_app = VersionedEntity.get_k8s_service_by_statefulset_id(
            self.version_id, self.resource_id)
        service_name = service_app.name
        db_config['spec']['serviceName'] = service_name

        # OnDelete 时删除 rollingUpdate
        update_strategy = db_config['spec']['updateStrategy']
        if update_strategy.get('type') == 'OnDelete':
            remove_key(update_strategy, 'rollingUpdate')
        elif update_strategy.get('type') == 'RollingUpdate':
            _roll = update_strategy['rollingUpdate']
            _roll['partition'] = handle_number_var(
                _roll['partition'], "%s[%s]partition" %
                                    (self.resource_name, self.resource_show_name),
                self.is_preview, self.is_validate)
        remove_key(db_config['spec'], 'strategy')
        return db_config


class K8sHPAGenerator(K8sProfileGenerator):
    resource_name = "K8sHPA"
    resource_sys_config = instance_constants.K8S_HPA_SYS_CONFIG


GENERATOR_DICT = {
    "application": ApplicationProfileGenerator,
    "deployment": DeploymentProfileGenerator,
    "service": ServiceProfileGenerator,
    "configmap": ConfigMapProfileGenerator,
    "secret": SecretProfileGenerator,
    "metric": MetricProfileGenerator,
    'hpa': HPAProfileGenerator,
    'ingress': IngressProfileGenerator,

    # k8s 相关资源
    "K8sSecret": K8sSecretGenerator,
    "K8sConfigMap": K8sConfigMapGenerator,
    "K8sService": K8sServiceGenerator,
    "K8sDeployment": K8sDeploymentGenerator,
    "K8sDaemonSet": K8sDaemonSetGenerator,
    "K8sJob": K8sJobGenerator,
    "K8sStatefulSet": K8sStatefulSetGenerator,
    "K8sIngress": K8sIngressGenerator,
    "K8sHPA": K8sHPAGenerator,
}
