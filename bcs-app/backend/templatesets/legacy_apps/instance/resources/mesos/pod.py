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
from backend.templatesets.legacy_apps.instance.resources import BCSResource, utils

SUPPORTED_HEALTH_CHECKS = ['HTTP', 'REMOTE_HTTP', 'TCP', 'REMOTE_TCP', 'COMMAND']


class Pod(BCSResource):
    def _health_checks_params_to_int(self, health_check, metadata_name, is_preview, is_validate):
        common_check_params = [
            'delaySeconds',
            'intervalSeconds',
            'timeoutSeconds',
            'consecutiveFailures',
            'gracePeriodSeconds',
        ]
        for p in common_check_params:
            health_check[p] = utils.handle_number_var(
                health_check[p], f'Application[{metadata_name}]{p}', is_preview, is_validate
            )

    def set_resources(self, resources):
        limits = resources.get('limits') or {}
        limits['cpu'] = str(limits.get('cpu') or '')
        limits['memory'] = str(limits.get('memory') or '')

        requests = resources.get('requests') or {}
        requests['cpu'] = str(requests.get('cpu') or '')
        requests['memory'] = str(requests.get('memory') or '')

    def set_health_checks(self, health_checks, metadata_name, is_preview, is_validate):
        if not health_checks:
            return

        # only one
        hc = health_checks[0]
        if hc.get('type') not in SUPPORTED_HEALTH_CHECKS:
            del health_checks[0]
            return

        self._health_checks_params_to_int(hc, metadata_name, is_preview, is_validate)
