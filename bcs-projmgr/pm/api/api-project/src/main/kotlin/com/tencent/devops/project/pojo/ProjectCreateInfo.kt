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

package com.tencent.devops.project.pojo

import io.swagger.annotations.ApiModel
import io.swagger.annotations.ApiModelProperty

@ApiModel("项目-新增模型")
data class ProjectCreateInfo(
    @ApiModelProperty("项目名称")
    val project_name: String,
    @ApiModelProperty("英文缩写")
    val english_name: String,
    @ApiModelProperty("项目类型")
    val project_type: Int,
    @ApiModelProperty("描述")
    val description: String = "",
    @ApiModelProperty("事业群ID")
    val bg_id: Long = 0,
    @ApiModelProperty("事业群名字")
    val bg_name: String = "",
    @ApiModelProperty("部门ID")
    val dept_id: Long =0,
    @ApiModelProperty("部门名称")
    val dept_name: String = "",
    @ApiModelProperty("中心ID")
    val center_id: Long = 0,
    @ApiModelProperty("中心名称")
    val center_name: String = "",
    @ApiModelProperty("是否保密")
    val is_secrecy: Boolean = false,
    @ApiModelProperty("kind")
    val kind: Int = 0
)