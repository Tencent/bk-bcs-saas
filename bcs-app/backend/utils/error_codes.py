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
import re
import copy

from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import APIException
from django.conf import settings


class APIError(APIException):
    """A common API Error
    需要继承APIException，否则在
    BrowsableAPIRenderer.show_form_for_method permissons异常无法捕获
    """

    delimiter = ": "

    def __init__(self, code):
        self.code_obj = code
        super(APIError, self).__init__(str(self))

    def __str__(self):
        """%s, print(), 使用"""
        return "%s: %s" % (self.code, self.message)

    def __repr__(self):
        """命令行查看使用"""
        return "<%s,%s>" % (self.code_obj.code_name, self.code)

    @property
    def message(self):
        return self.code_obj.message

    @property
    def code(self):
        return self.code_obj.code

    @property
    def status_code(self):
        return self.code_obj.status_code

    def format(self, message=None, replace=False, **kwargs):
        """Using a customized message for this ErrorCode

        :param str message: if not given, default message will be used
        :param bool replace: relace default message if true
        """
        self.code_obj = copy.copy(self.code_obj)
        if message:
            if replace:
                self.code_obj.message = message
            else:
                self.code_obj.message += "%s%s" % (self.delimiter, message)

        # Render message string
        if kwargs:
            self.code_obj.message = self.code_obj.message.format(**kwargs)

        return self

    def f(self, message=None, **kwargs):
        return self.format(message=message, **kwargs)

    def __call__(self, message=None, *args, **kwargs):
        """init api error"""
        self.code_obj = copy.copy(self.code_obj)
        if message:
            self.code_obj.message = message

        # Render prompt string
        if args:
            self.code_obj.message = self.code_obj.message % args
        if kwargs:
            self.code_obj.message = self.code_obj.message % kwargs

        return self


class ErrorCode(object):
    """Error code"""

    def __init__(self, code_name, code, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.code_name = code_name
        self.code = code
        self.message = message
        self.status_code = status_code


class ErrorCodeCollection(object):
    """A collection of ErrorCodes"""

    def __init__(self):
        self._error_codes_dict = {}

    def add_code(self, error_code):
        self._error_codes_dict[error_code.code_name] = error_code

    def add_codes(self, code_list):
        for error_code in code_list:
            self._error_codes_dict[error_code.code_name] = error_code

    def __getattr__(self, code_name):
        error_code = self._error_codes_dict[code_name]
        return APIError(error_code)

    def __dir__(self):
        return self._error_codes_dict.keys()


error_codes = ErrorCodeCollection()


# API使用
error_codes.add_codes(
    [
        ErrorCode("APIError", 40001, _("请求失败")),
        ErrorCode("NoBCSService", 416, _("该项目没有使用蓝鲸容器服务")),
        ErrorCode("ValidateError", 40002, _("参数不正确")),
        ErrorCode("ComponentError", 40003, _("第三方接口调用失败")),
        ErrorCode("JsonFormatError", 40004, _("json格式错误")),
        ErrorCode("ParamMissError", 40005, _("参数缺失")),
        ErrorCode("CheckFailed", 40006, _("校验失败")),
        ErrorCode("ExpiredError", 40007, _("资源已过期")),
        ErrorCode("IPPermissionDenied", 40008, _("没有主机使用权限")),
        # Helm相关错误码(前端已经在使用)
        ErrorCode("HelmNoRegister", 40031, _("集群未注册")),
        ErrorCode("HelmNoNode", 40032, _("集群下没有节点")),
        # 功能暂未开放
        ErrorCode("NotOpen", 40040, _("功能正在建设中")),
        # 未登入, 只是定义，一般不需要使用
        ErrorCode("Unauthorized", 40101, _("用户未登录或登录态失效，请使用登录链接重新登录"), status.HTTP_401_UNAUTHORIZED),
        # 没有权限，最好使用drf permission class检查权限
        ErrorCode("Forbidden", 40301, _("没有使用权限"), status.HTTP_403_FORBIDDEN),
        # 权限中心错误码
        ErrorCode("IAMCheckFailed", 40302, _("权限校验失败"), status.HTTP_403_FORBIDDEN),
        # 资源未找到
        ErrorCode("ResNotFoundError", 40400, _("资源未找到"), status.HTTP_404_NOT_FOUND),
    ]
)

bk_error_codes = ErrorCodeCollection()
# 打印日志使用, 1402是分配给BCS SaaS使用
bk_error_codes.add_codes(
    [
        ErrorCode("ConfigError", 1402400, _("配置{}错误")),
        # 权限中心API调用错误
        ErrorCode("IAMError", 1402100, _("权限中心接口调用失败:")),
        # 仓库API调用错误
        ErrorCode("DepotError", 1402101, _("仓库接口调用失败:")),
        # 消息管理API调用错误，请按ESB的错误码指引排查
        ErrorCode("CmsiError", 1402102, _("消息管理CMSI接口调用失败:")),
        # 蓝鲸登录平台API调用错误，请按ESB的错误码指引排查
        ErrorCode("BkLoginError", 1402103, _("蓝鲸登录平台接口调用失败:")),
    ]
)
