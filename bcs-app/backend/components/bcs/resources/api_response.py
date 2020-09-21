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
from functools import wraps

from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

DEFAULT_ERROR_CODE = 4001
DEFAULT_SUCCESS_CODE = 0


# 兼容view层的逻辑
# 先前在view层是这样判断的
# if not resp.get('code'):  raise xxx
def response(format_data=True):
    def decorator(func):
        @wraps(func)
        def _wrapped_func(*args, **kwargs):
            try:
                data = func(*args, **kwargs)
                if format_data:
                    data = data.to_dict()
                return {
                    'code': DEFAULT_SUCCESS_CODE,
                    'result': True,
                    'data': data,
                    'message': 'success'
                }
            except ApiException as err:
                try:
                    if err.status == 404:
                        logger.info('resource not found, %s', err)
                    else:
                        logger.error('request bcs api error, %s', err)
                    message = json.loads(err.body)['message']
                except Exception:
                    message = f'request bcs api error, {err}'
                return {
                    'code': DEFAULT_ERROR_CODE,
                    'result': False,
                    'message': message
                }
            except Exception as err:
                logger.exception('request bcs api error, %s', err)
                return {
                    'code': DEFAULT_ERROR_CODE,
                    'result': False,
                    'message': err
                }
        return _wrapped_func
    return decorator
