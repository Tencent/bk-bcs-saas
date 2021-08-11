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

Usage: python manage.py init_mesos_image_secret -n '合法的 access_token'
"""
from django.core.management.base import BaseCommand

from backend.apps import constants
from backend.components import paas_cc
from backend.templatesets.legacy_apps.configuration.namespace.views import NamespaceBase


class Command(BaseCommand):
    help = u"初始化MESOS命名空间的 image secret"

    def add_arguments(self, parser):

        parser.add_argument(
            '-n',
            '--access_token',
            action='store',
            dest='access_token',
            default='',
            help='access_token',
        )

    def handle(self, *args, **options):
        """用到了 paas_cc 的两个API，必须要带用户登录态的accesstoken才可以"""
        print(options)
        if options.get('access_token'):
            access_token = options['access_token']
        else:
            return False
        # 获取所有的项目信息
        pro_res = paas_cc.get_projects(access_token)
        pro_data = pro_res.get('data') or []

        init_ns = 0
        has_init = 0
        error_list = []
        for _d in pro_data:
            # 只需要处理 mesos 项目
            _kind = _d.get('kind')
            if _kind != 2:
                continue

            project_id = _d.get('project_id')
            project_code = _d.get('english_name')
            self.stdout.write(self.style.SUCCESS("init project:%s" % project_code))
            # 查询项目下的所有命名空间
            ns_result = paas_cc.get_namespace_list(access_token, project_id, limit=constants.ALL_LIMIT)
            ns_res = ns_result.get('data') or {}
            ns_data = ns_res.get('results') or []

            for _ns in ns_data:
                has_image_secret = _ns.get('has_image_secret')
                # 已经初始化过的则不再初始化
                if has_image_secret:
                    has_init = has_init + 1
                    continue

                cluster_id = _ns.get('cluster_id')
                ns_name = _ns.get('name')
                namespace_id = _ns.get('id')
                ns_base = NamespaceBase()
                try:
                    ns_base.init_mesos_ns_by_bcs(access_token, project_id, project_code, cluster_id, ns_name)
                except Exception:
                    error_list.append('%s[%s]' % (ns_name, namespace_id))
                    self.stdout.write(
                        self.style.WARNING("error init image secret in ns: %s[%s]" % (ns_name, namespace_id))
                    )
                else:
                    # 更新
                    paas_cc.update_namespace(access_token, project_id, namespace_id, has_image_secret=True)
                    self.stdout.write(self.style.SUCCESS("init image secret in ns: %s[%s]" % (ns_name, namespace_id)))
                    init_ns = init_ns + 1
        self.stdout.write(self.style.WARNING("error_list:%s" % ','.join(error_list)))
        self.stdout.write(
            self.style.SUCCESS("init end, init_ns:%s, has_init:%s, error:%s" % (init_ns, has_init, len(error_list)))
        )
