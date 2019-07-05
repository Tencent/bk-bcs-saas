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
import re
import yaml
import inspect
from Crypto.PublicKey import RSA

import jsonschema

from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
from rest_framework import serializers, fields
import six

from backend.utils.sanitizer import clean_html


class MaskField(serializers.CharField):
    """掩码字段: 只匹配符合正则规则的字符"""
    REGEX = re.compile(".")

    def to_internal_value(self, data):
        data = super(MaskField, self).to_internal_value(data)
        data = data.strip()
        return "".join(self.REGEX.findall(data))


class NickNameField(MaskField):
    """
    名称字段，过滤[中文\w+\-\_]字符集
    test: print "".join(re.compile(u"[\u4300-\u9fa5\w\_\-]+").findall(u"a中文 字母 - ——"))
    """
    REGEX = re.compile(u"[\u4e00-\u9fa5\w\-\_]")


class ChineseField(MaskField):
    """
    中文字段
    """
    REGEX = re.compile(u"[\u4e00-\u9fa5\w\-\_\；\？\。\—\…\《\》\“\”\.\,\s\?\'\"\;\‘\’\r\n]")


class RichTextField(serializers.CharField):
    """
    富文本字段，带XSS过滤供
    """

    def to_internal_value(self, data):
        data = super(RichTextField, self).to_internal_value(data)
        return clean_html(data)


def patch_datetime_field():
    """Patch DateTimeField which respect current timezone
    See also: https://github.com/encode/django-rest-framework/issues/3732
    """

    def to_representation(self, value):
        # This is MAGICK!
        if value and settings.USE_TZ:
            try:
                value = timezone.localtime(value)
            except ValueError:
                pass
        return orig_to_representation(self, value)

    orig_to_representation = fields.DateTimeField.to_representation
    fields.DateTimeField.to_representation = to_representation


class YamlField(serializers.CharField):
    def run_validation(self, data=""):
        if inspect.isclass(data):
            return ""

        try:
            yaml.load(data)
        except yaml.error.YAMLError as e:
            raise serializers.ValidationError("invalidated yaml, %s" % e)
        return super(YamlField, self).run_validation(data)


class JsonSchemaField(serializers.JSONField):
    JSONSCHEMA = {}

    def run_validation(self, data=""):
        if inspect.isclass(data):
            return ""

        if isinstance(data, (bytes, str)):
            try:
                data = json.loads(data)
            except yaml.scanner.ScannerError as e:
                raise serializers.ValidationError("invalidated json field")

        try:
            jsonschema.validate(data, self.JSONSCHEMA)
        except jsonschema.ValidationError as e:
            raise serializers.ValidationError("jsonschema validated failed, %s" % e.message)

        return super(JsonSchemaField, self).run_validation(data)


class HelmValueField(JsonSchemaField):
    JSONSCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
                "value": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "integer"},
                        {"type": "boolean"},
                        {"type": "number"},
                    ]
                },
                "type": {
                    "type": "string",
                },
            }
        }
    }


class CryptoField(serializers.HiddenField):
    """实现安全数据写入"""

    def to_internal_value(self, encrypted_text):
        pri_key = RSA.importKey(settings.HELM_RSA_PRIVATE)
        decrypted_text = pri_key.decrypt(encrypted_text)
        return decrypted_text
