/*
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 *
 */

package com.tencent.devops.project.pojo.user

import io.swagger.annotations.ApiModel
import io.swagger.annotations.ApiModelProperty

@ApiModel("用户-信息模型")
data class UserVO(
    @ApiModelProperty("中文名")
    var chinese_name: String,
    @ApiModelProperty("头像URL")
    val avatar_url: String?,
    @ApiModelProperty("bkpaas用户ID")
    val bkpaas_user_id: String?,
    @ApiModelProperty("用户名")
    var username: String,
    @ApiModelProperty("权限")
    val permissions: String?
)