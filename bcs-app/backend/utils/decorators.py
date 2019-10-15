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
import time
from functools import wraps

import six
from django.utils.encoding import force_str
from requests.models import Response

from backend.utils.exceptions import ComponentError

logger = logging.getLogger(__name__)

# 格式化方法
FORMAT_FUNC = {
    'json': json.loads,
}

# 最大返回字符数
MAX_RESP_TEXT_SIZE = 1000

def curl_log(func):
    """http请求添加curl log
    """

    @wraps(func)
    def _wrapped_func(*args, **kwargs):
        st = time.time()
        resp = func(*args, **kwargs)

        requests_curl_log(resp, st)

        return resp
    return _wrapped_func


def requests_curl_log(resp, st):
    """记录requests curl log
    """
    if not isinstance(resp, Response):
        raise ValueError("返回值【%s】必须是Respose对象" % resp)

    # 添加日志信息
    curl_req = "REQ: curl -X {method} '{url}'".format(method=resp.request.method, url=resp.request.url)

    if resp.request.body:
        curl_req += " -d '{body}'".format(body=force_str(resp.request.body))

    if resp.request.headers:
        for header in resp.request.headers.items():
            # ignore headers
            if header[0] in ['User-Agent', 'Accept-Encoding', 'Connection', 'Accept', 'Content-Length']:
                continue
            if header[0] == 'Cookie' and header[1].startswith('x_host_key'):
                continue
            curl_req += " -H '{k}: {v}'".format(k=header[0], v=header[1])

    if len(resp.text) > MAX_RESP_TEXT_SIZE:
        resp_text = f"{resp.text[:MAX_RESP_TEXT_SIZE]}..."
    else:
        resp_text = resp.text

    curl_resp = 'RESP: [%s] %.2fms %s' % (resp.status_code, (time.time() - st) * 1000, resp_text)

    logger.info('%s\n \t %s', curl_req, curl_resp)

    # bcs log
    if 'bcs_api' in resp.request.url:
        # bcs 返回错误状态吗 或错误消息时记录 error日志
        if resp.status_code != 200 or resp.text.find('"result":false') >= 0:
            bcs_req = 'bcs_api error: %s' % curl_req
            bcs_resp = 'bcs_api error: %s' % curl_resp
            logger.error('%s\n \t %s', bcs_req, bcs_resp)
        else:
            bcs_req = 'bcs_api: %s' % curl_req
            bcs_resp = 'bcs_api: %s' % curl_resp
            logger.info('%s\n \t %s', bcs_req, bcs_resp)


def response(f=None):
    """返回值格式化
    """

    def decorator(func):
        @wraps(func)
        def _wrapped_func(*args, **kwargs):
            resp = func(*args, **kwargs)
            format_func = FORMAT_FUNC.get(f)
            if format_func:
                # 获取内容
                if isinstance(resp, Response):
                    content = resp.text
                elif isinstance(resp, six.string_types):
                    content = resp
                else:
                    raise ValueError(u"返回值【%s】必须是字符串或者Respose对象" % resp)

                # 解析格式
                err_msg = kwargs.get('err_msg', None)
                try:
                    resp = format_func(content)
                except Exception as error:
                    logger.exception(
                        "请求第三方失败，使用【%s】格式解析 %s 异常，%s", f, content, error)
                    raise ComponentError(err_msg or error)

            return resp
        return _wrapped_func
    return decorator
