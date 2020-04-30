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

from django.utils.translation import ugettext_lazy as _

from .constants import VariableScope, VariableCategory
from .models import Variable, NameSpaceVariable, ClusterVariable

SCOPES = {
    'ns_vars': VariableScope.NAMESPACE.value,
    'cluster_vars': VariableScope.CLUSTER.value,
    'global_vars': VariableScope.GLOBAL.value
}


def _import_var(username, project_id, var, scope_key):
    scope_vars = var.pop(scope_key, None)
    try:
        vobj = Variable.objects.get(project_id=project_id, key=var['key'])
    except Variable.DoesNotExist:
        var.update({
            'project_id': project_id,
            'default': json.dumps({'value': var['value']}),
            'category': VariableCategory.CUSTOM.value,
            'scope': SCOPES[scope_key],
            'creator': username,
            'updator': username
        })
        del var['value']
        vobj = Variable.objects.create(**var)
    else:
        if vobj.scope != SCOPES[scope_key]:
            raise Exception(_("不能更改原有变量key({})的作用范围({})").format(vobj.key, vobj.scope))
        vobj.name = var['name']
        vobj.default = json.dumps({'value': var['value']})
        vobj.desc = var['desc']
        vobj.updator = username
        vobj.save()
    return vobj, scope_vars


def _import_global_var(username, project_id, var):
    _import_var(username, project_id, var, 'global_vars')


def _import_ns_var(username, project_id, var):
    vobj, ns_vars = _import_var(username, project_id, var, 'ns_vars')
    NameSpaceVariable.batch_save_by_var_id(
        vobj, var_dict={v['ns_id']: v.get('value') for v in ns_vars}
    )


def _import_cluster_var(username, project_id, var):
    vobj, cluster_vars = _import_var(username, project_id, var, 'cluster_vars')
    ClusterVariable.batch_save_by_var_id(
        vobj, var_dict={v['cluster_id']: v['value'] for v in cluster_vars}
    )


def import_vars(username, project_id, vars):
    for v in vars:
        if 'cluster_vars' in v:
            _import_cluster_var(username, project_id, v)
            continue
        if 'ns_vars' in v:
            _import_ns_var(username, project_id, v)
            continue
        _import_global_var(username, project_id, v)
