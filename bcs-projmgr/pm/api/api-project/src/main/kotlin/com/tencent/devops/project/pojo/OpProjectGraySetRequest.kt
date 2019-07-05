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

import com.fasterxml.jackson.annotation.JsonProperty
import io.swagger.annotations.ApiModel
import io.swagger.annotations.ApiModelProperty

/**
 * 灰度项目设置请求实体
 * author: carlyin
 * since: 2018-12-18
 */
@ApiModel("灰度项目设置请求实体")
data class OpProjectGraySetRequest(
    @JsonProperty(value = "operateFlag", required = true)
    @ApiModelProperty("操作标识 1：设置灰度 2：取消灰度")
    val operateFlag: Int,
    @JsonProperty(value = "projectCodeList", required = true)
    @ApiModelProperty("项目编码集合")
    val projectCodeList: List<String>
)
