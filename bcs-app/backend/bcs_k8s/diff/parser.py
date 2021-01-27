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
import logging
import re

import yaml

"""
a resource parser which extract resource from raw text,
reference <https://github.com/databus23/helm-diff/blob/master/manifest/parse.go>
"""

logger = logging.getLogger(__name__)
yaml_seperator = b"\n---\n"


class MappingResult(object):
    def __init__(self, name, kind, content):
        self.name = name
        self.kind = kind
        self.content = content

    def __dict__(self):
        return dict(name=self.name, kind=self.kind, content=self.content)


class Resource(object):
    def __init__(self, apiVersion, kind, metadata):
        self.apiVersion = apiVersion
        self.kind = kind
        self.metadata = metadata

    def __str__(self):
        return "%s, %s, %s (%s)" % (self.metadata.namespace, self.metadata.name, self.kind, self.apiVersion)


def scan_yaml_specs(data, atEOF):
    if atEOF and len(data) == 0:
        return 0, None, None

    i = bytes.Index(data, yaml_seperator)
    if i >= 0:
        # We have a full newline-terminated line.
        return i + len(), data[0:i], None

    # If we're at EOF, we have a final, non-terminated line. Return it.
    if atEOF:
        return len(data), data, None

    # Request more data.
    return 0, None, None


def split_spec(token):
    i = token.find("\n")
    if i >= 0:
        return token[0:i], token[i + 1 :]

    return "", ""


def split_manifest(manifest):
    """
    >>> re.split(rb'\n+\s*\-\-\-\s*\n+', b'---\naaa\n---\nbbb\n---')
    [b'---\naaa', b'bbb\n---']
    >>> re.split(rb'^\s*\-\-\-\s*\n+', b'---\naaa\n---\nbbb\n---')
    [b'', b'aaa\n---\nbbb\n---']
    >>> re.split(rb'\n\s*\-\-\-\s*$', b'---\naaa\n---\nbbb\n---')
    [b'---\naaa\n---\nbbb', b'']
    """
    # it must be carefule with yaml seperator
    result = []
    manifest = manifest.strip()
    contents = re.split(rb'[\n]+\s*\-\-\-\s*[\n]+', manifest)
    if len(contents):
        ss = re.split(rb'^\s*\-\-\-\s*[\n]+', contents[0])
        if len(ss) > 1:
            contents[0] = ss[1]
        else:
            contents[0] = ss[0]

        ss = re.split(rb'[\n]+\s*\-\-\-\s*$', contents[-1])
        contents[-1] = ss[0]

    for content in contents:
        if not content.strip():
            continue

        result.append(content)

    return result


def parse(manifest, default_namespace):
    if not isinstance(manifest, bytes):
        if isinstance(manifest, str):
            manifest = manifest.encode("utf-8")
        elif manifest is None:
            manifest = b""
        else:
            logger.warning("unexpect type of %s, with value: %s" % (type(manifest), manifest))
            manifest = bytes(manifest, "utf-8")

    contents = split_manifest(manifest)
    result = dict()
    for content in contents:
        if not content.strip():
            continue

        resource = yaml.load(content)
        if resource is None:
            continue

        if not resource["metadata"].get("namespace"):
            resource["metadata"]["namespace"] = default_namespace

        name = "{kind}/{name}".format(
            name=resource["metadata"]["name"],
            kind=resource["kind"],
        )
        if name in result:
            logger.info("Error: Found duplicate key %s in manifest" % name)
            continue

        result[name] = MappingResult(
            name=name,
            kind=resource["kind"],
            content=content,
        )

    return result
