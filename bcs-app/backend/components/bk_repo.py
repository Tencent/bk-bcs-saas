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

from django.conf import settings

from backend.utils.requests import bk_post
from backend.utils.decorators import parse_response_data

logger = logging.getLogger(__name__)

# 镜像API在apigw上注册的地址
BK_REPO_API_PREFIX = f"{settings.BK_REPO_API_PREFIX}/{settings.BK_REPO_STAG}"
IMAGE_API_PREFIX = f"{BK_REPO_API_PREFIX}/dockerapi/api/image"
REPO_API_PREFIX = f"{BK_REPO_API_PREFIX}/dockerapi/api/repo"


def _headers(access_token):
    return {
        "X-BKAPI-AUTHORIZATION": json.dumps({
            "access_token": access_token
        })
    }


def api_request(access_token, url, data=None):
    return bk_post(url, json=data, headers=_headers(access_token))


def query_public_images(access_token, search_name=None, page_num=1, page_size=100):
    """查询公共仓库镜像
    """
    url = f"{IMAGE_API_PREFIX}/queryPublicImage"
    data = {
        "searchKey": search_name,
        "pageNumber": page_num,
        "pageSize": page_size
    }
    return api_request(access_token, url, data=data)


def query_project_images(access_token, project_code, search_name=None, page_num=1, page_size=100):
    """查询项目下的镜像
    """
    url = f"{IMAGE_API_PREFIX}/queryProjectImage"
    data = {
        "projectId": project_code,
        "searchKey": search_name,
        "pageNumber": page_num,
        "pageSize": page_size
    }
    return api_request(access_token, url, data=data)


def query_image_tags(access_token, project_code, image_name, page_num=1, page_size=100):
    url = f"{IMAGE_API_PREFIX}/queryImageTag"
    data = {
        "projectId": project_code,
        "imageRepo": image_name,
        "pageNumber": page_num,
        "pageSize": page_size
    }
    return api_request(access_token, url, data=data)


def create_repo(access_token, project_code):
    """创建仓库
    """
    url = f"{REPO_API_PREFIX}/create/{project_code}"
    return api_request(access_token, url)


def create_account(access_token, project_code):
    url = f"{REPO_API_PREFIX}/account/create/{project_code}"
    return api_request(access_token, url)
