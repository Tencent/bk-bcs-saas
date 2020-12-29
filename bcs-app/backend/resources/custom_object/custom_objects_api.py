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
from six import iteritems

from kubernetes import client


class CustomObjectsApi(client.CustomObjectsApi):
    """
    select_header_content_type默认为application/json-patch+json
    """

    def patch_namespaced_custom_object_with_http_info(self, group, version, namespace, plural, name, body, **kwargs):
        all_params = ["group", "version", "namespace", "plural", "name", "body"]
        all_params.append("async_req")
        all_params.append("_return_http_data_only")
        all_params.append("_preload_content")
        all_params.append("_request_timeout")

        params = locals()
        for key, val in iteritems(params["kwargs"]):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'" " to method patch_namespaced_custom_object" % key
                )
            params[key] = val
        del params["kwargs"]
        # verify the required parameter 'group' is set
        if ("group" not in params) or (params["group"] is None):
            raise ValueError("Missing the required parameter `group` when calling `patch_namespaced_custom_object`")
        # verify the required parameter 'version' is set
        if ("version" not in params) or (params["version"] is None):
            raise ValueError("Missing the required parameter `version` when calling `patch_namespaced_custom_object`")
        # verify the required parameter 'namespace' is set
        if ("namespace" not in params) or (params["namespace"] is None):
            raise ValueError(
                "Missing the required parameter `namespace` when calling `patch_namespaced_custom_object`"
            )
        # verify the required parameter 'plural' is set
        if ("plural" not in params) or (params["plural"] is None):
            raise ValueError("Missing the required parameter `plural` when calling `patch_namespaced_custom_object`")
        # verify the required parameter 'name' is set
        if ("name" not in params) or (params["name"] is None):
            raise ValueError("Missing the required parameter `name` when calling `patch_namespaced_custom_object`")
        # verify the required parameter 'body' is set
        if ("body" not in params) or (params["body"] is None):
            raise ValueError("Missing the required parameter `body` when calling `patch_namespaced_custom_object`")

        collection_formats = {}

        path_params = {}
        if "group" in params:
            path_params["group"] = params["group"]
        if "version" in params:
            path_params["version"] = params["version"]
        if "namespace" in params:
            path_params["namespace"] = params["namespace"]
        if "plural" in params:
            path_params["plural"] = params["plural"]
        if "name" in params:
            path_params["name"] = params["name"]

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if "body" in params:
            body_params = params["body"]
        # HTTP header `Accept`
        header_params["Accept"] = self.api_client.select_header_accept(["application/json"])

        # HTTP header `Content-Type`
        header_params["Content-Type"] = self.api_client.select_header_content_type(
            ["application/json-patch+json", "application/merge-patch+json", "application/strategic-merge-patch+json"]
        )

        # Authentication setting
        auth_settings = ["BearerToken"]

        return self.api_client.call_api(
            "/apis/{group}/{version}/namespaces/{namespace}/{plural}/{name}",
            "PATCH",
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type="object",
            auth_settings=auth_settings,
            async_req=params.get("async_req"),
            _return_http_data_only=params.get("_return_http_data_only"),
            _preload_content=params.get("_preload_content", True),
            _request_timeout=params.get("_request_timeout"),
            collection_formats=collection_formats,
        )
