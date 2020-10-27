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
import base64
import logging

from django.utils.translation import ugettext_lazy as _

from backend.components import bk_repo
from backend.utils.error_codes import error_codes, bk_error_codes
from backend.utils.errcodes import ErrorCode

logger = logging.getLogger(__name__)


def get_jfrog_account(access_token, project_code, project_id, is_bk=False):
    """
    获取项目的镜像账号
    """
    account = bk_repo.create_account(access_token, project_code)
    # 兼容先前返回{"user": "", "password": ""}
    account["user"] = account["userId"]
    return account


def get_bk_jfrog_auth(access_token, project_code, project_id):
    jfrog_account = get_jfrog_account(
        access_token, project_code, project_id, is_bk=True)
    user_pwd = "%s:%s" % (jfrog_account.get(
        'user'), jfrog_account.get('password'))
    user_auth = {
        "auth": base64.b64encode(
            user_pwd.encode(encoding="utf-8")).decode()
    }
    return user_auth


def upload_image_api(request, project_id, image_data):
    """
    上传镜像
    TODO: API 暂未提供该功能
    """
    raise error_codes.NotOpen(_("上传镜像功能正在建设中"))


def get_upload_status_api(request, project_id, task_id):
    """查询上传状态
    TODO: API 暂未提供该功能
    """
    raise error_codes.NotOpen(_("上传镜像功能正在建设中"))


def trans_paging_query(query):
    """
    将前端的分页信息转换为haobor API需要的:page\pageSize
    该方法只在本文件内调用
    """
    start = query.get('start')
    limit = query.get('limit')
    if start is not None and limit is not None:
        page_size = limit
        page = (start // page_size) + 1
        query['page'] = page
        query['pageSize'] = page_size
    else:
        # 不分页的地方给默认值
        query['page'] = 1
        query['pageSize'] = 100
    return query


def refine_images(images):
    records = images.pop("records", [])
    images["total"] = images["totalRecords"]
    for record in records:
        record["repo"] = record["imageName"]
        record["name"] = record["imagePath"]
    images["imageList"] = records
    return images


def _repo_response(data):
    """兼容上层
    """
    return {"code": ErrorCode.NoError, "data": data}


def get_public_image_list(query):
    """
    获取公共镜像列表
    """
    query = trans_paging_query(query)
    images = bk_repo.query_public_images(
        query["access_token"],
        search_name=query.get("searchKey", ""),
        page_num=query["page"],
        page_size=query["pageSize"]
    )
    return _repo_response(refine_images(images))


def get_project_image_list(query):
    """
    获取项目镜像列表
    """
    query = trans_paging_query(query)
    images = bk_repo.query_project_images(
        query["access_token"],
        query["project_code"],
        search_name=query.get("searchKey", ""),
        page_num=query["page"],
        page_size=query["pageSize"]
    )
    return _repo_response(refine_images(images))


def get_image_tags(access_token, project_id, project_code, offset, limit, **query_params):
    """获取镜像信息和tag列表
    """
    project_code = "public" if query_params.get("is_public") else project_code
    tags = bk_repo.query_image_tags(
        access_token,
        project_code,
        image_name=query_params.get("imageRepo", ""),
        page_num=offset,
        page_size=limit
    )
    tags["has_previous"] = False
    tags["has_next"] = False
    records = tags.pop("records", [])
    for record in records:
        # 外部版本只有一套仓库
        record["artifactorys"] = ["PROD"]
        record["repo"] = record["imageName"]
        record["name"] = record["imagePath"]
    tags["tags"] = records
    return _repo_response(tags)


def get_pub_or_project_image_tags(query, project_code="public"):
    tags = bk_repo.query_image_tags(
        query["access_token"],
        project_code,
        image_name=query.get("imageRepo", "")
    )
    records = tags.pop("records", [])
    for record in records:
        record["repo"] = record["imageName"]
        record["name"] = record["imagePath"]
    tags["tags"] = records
    return _repo_response([tags])


def get_pub_image_info(query):
    """公共获镜像详情（tag列表信息)
    """
    return get_pub_or_project_image_tags(query)


def get_project_image_info(query):
    """
    获取项目镜像详情（tag列表信息）
    """
    return get_pub_or_project_image_tags(query, project_code=query["project_code"])


def create_project_path_by_api(access_token, project_id, project_code):
    """调用仓库API创建项目仓库路径
    {
        "result": true,
        "message": "success",
        "data": {
            "project_id": 6,
            "name": "test",
            "creation_time": "2018-12-25 16:13:10",
            "update_time": "2018-12-25 16:13:10",
            "repo_count": 2
        },
        "code": 0
    }
    """
    return bk_repo.create_repo(access_token, project_code)
