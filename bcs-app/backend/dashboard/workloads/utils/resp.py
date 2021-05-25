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
from typing import Dict

from attr import dataclass

from backend.utils.basic import get_with_placeholder, getitems
from backend.utils.error_codes import error_codes


@dataclass
class ContainerRespBuilder:
    """ 通过 Pod 配置信息获取容器信息 """

    pod: Dict
    container_id: str = None

    def build_list(self):
        """ 构造列表展示的容器信息 """
        containers = []
        for s in getitems(self.pod, 'status.containerStatuses', []):
            status = message = reason = None
            # state 有且只有一对键值：running / terminated / waiting
            # https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.21/#containerstate-v1-core
            for k, v in s['state'].items():
                status = k
                message = v.get('message') or k
                reason = v.get('reason') or k

            containers.append(
                {
                    # 原格式：docker://[a-zA-Z0-9]{64}，需要去除前缀
                    'container_id': (s['containerID'] or '').split('//')[-1],
                    'image': s['image'],
                    'name': s['name'],
                    'status': status,
                    'message': message,
                    'reason': reason,
                }
            )
        return containers

    def build(self):
        """ 构造展示用的容器详情信息 """
        for cs in getitems(self.pod, 'status.containerStatuses', []):
            if self.container_id in cs['containerID']:
                container_status = cs
                break
        else:
            raise error_codes.RecordNotFound.f(f'容器 {self.container_id} 状态信息不存在')

        labels = getitems(self.pod, 'metadata.labels', {})
        spec, status = self.pod['spec'], self.pod['status']
        # {container_name: container_spec}
        container_spec_map = {s['name']: s for s in spec.get('containers') or []}
        container_spec = container_spec_map[container_status['name']]

        return {
            'host_name': get_with_placeholder(spec, 'nodeName'),
            'host_ip': get_with_placeholder(status, 'hostIP'),
            'container_ip': get_with_placeholder(status, 'podIP'),
            'container_id': self.container_id,
            'container_name': get_with_placeholder(container_status, 'name'),
            'image': get_with_placeholder(container_status, 'image'),
            'network_mode': get_with_placeholder(spec, 'dnsPolicy'),
            # 端口映射
            'ports': container_spec.get('ports', []),
            # 命令
            'command': {
                'command': get_with_placeholder(container_spec, 'command', ''),
                'args': ' '.join(container_spec.get('args', [])),
            },
            # 挂载卷
            'volumes': [
                {
                    'host_path': get_with_placeholder(mount, 'name'),
                    'mount_path': get_with_placeholder(mount, 'mountPath'),
                    'readonly': get_with_placeholder(mount, 'readOnly'),
                }
                for mount in container_spec.get('volumeMounts', [])
            ],
            # 标签
            'labels': [{'key': key, 'val': val} for key, val in labels.items()],
            # 资源限制
            'resources': container_spec.get('resources', {}),
        }
