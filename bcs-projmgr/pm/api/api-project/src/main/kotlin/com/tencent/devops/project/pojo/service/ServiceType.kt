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
@ApiModel("服务类型-显示模型")
data class ServiceType(
    @ApiModelProperty("主键ID")
    val id: Long,
    @ApiModelProperty("服务类型名称")
    val title: String,
    @ApiModelProperty("权重")
    val weight: Int,
    @ApiModelProperty("创建人")
    val createUser: String?,
    @ApiModelProperty("创建时间")
    val createTime: String?,
    @ApiModelProperty("修改人")
    val updateUser: String?,
    @ApiModelProperty("修改时间")
    val updateTime: String?
)