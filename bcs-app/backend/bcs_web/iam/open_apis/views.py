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
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.utils.renderers import BKAPIRenderer

from .authentication import IamBasicAuthentication
from .resources.provider import BCSResourceProvider
from .serializers import QueryResourceSLZ


class ResourceAPIView(APIView):
    renderer_classes = (BKAPIRenderer,)
    authentication_classes = (IamBasicAuthentication,)
    permission_classes = ()

    def _get_options(self, request):
        language = request.META.get("HTTP_BLUEKING_LANGUAGE", "zh-cn")
        if language == "zh-cn":
            request.LANGUAGE_CODE = "zh-hans"
        else:
            request.LANGUAGE_CODE = "en"
        return {"language": language}

    def post(self, request):
        serializer = QueryResourceSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        provider = BCSResourceProvider(resource_type=validated_data["type"])
        resp = provider.provide(validated_data, **self._get_options(request))
        return Response(resp)
