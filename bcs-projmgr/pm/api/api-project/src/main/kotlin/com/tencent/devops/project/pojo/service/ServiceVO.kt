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

@ApiModel("服务-显示模型")
data class ServiceVO(
    @ApiModelProperty("主键ID")
    val id: Long,
    @ApiModelProperty("名称")
    val name: String,
    @ApiModelProperty("链接")
    val link: String,
    @ApiModelProperty("新链接")
    val link_new: String,
    @ApiModelProperty("状态")
    val status: String,
    @ApiModelProperty("注入类型")
    val inject_type: String,
    @ApiModelProperty("框架URL")
    val iframe_url: String,
    @ApiModelProperty("cssURL")
    val css_url: String,
    @ApiModelProperty("jsURL")
    val js_url: String,
    @ApiModelProperty("显示项目列表")
    val show_project_list: Boolean,
    @ApiModelProperty("显示导航")
    val show_nav: Boolean,
    @ApiModelProperty("项目ID类型")
    val project_id_type: String,
    @ApiModelProperty("是否收藏")
    val collected: Boolean,
    @ApiModelProperty("权重")
    val weigHt: Int
)