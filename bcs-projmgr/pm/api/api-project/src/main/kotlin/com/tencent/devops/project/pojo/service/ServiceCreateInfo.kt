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

package com.tencent.devops.project.pojo.service

import io.swagger.annotations.ApiModel
import io.swagger.annotations.ApiModelProperty

/**
 * @author eltons,  Date on 2018-12-05.
 */
@ApiModel("服务-创建模型")
data class ServiceCreateInfo(
    @ApiModelProperty("服务名称", required = true)
    val name: String,
    @ApiModelProperty("服务类型ID", required = true)
    val serviceTypeId: Long,
    @ApiModelProperty("是否在页面显示")
    val showProjectList: Boolean = true,
    @ApiModelProperty("showNav")
    val showNav: Boolean = true,
    @ApiModelProperty("状态（是否默认显示灰色）")
    val status: String = "ok",

    @ApiModelProperty("链接1")
    val link: String?,
    @ApiModelProperty("链接2")
    val linkNew: String?,
    @ApiModelProperty("注入类型")
    val injectType: String?,
    @ApiModelProperty("iframeUrl")
    val iframeUrl: String?,
    @ApiModelProperty("cssUrl")
    val cssUrl: String?,
    @ApiModelProperty("jsUrl")
    val jsUrl: String?,
    @ApiModelProperty("projectIdType")
    val projectIdType: String?,
    @ApiModelProperty("权重")
    val weight: Int
)