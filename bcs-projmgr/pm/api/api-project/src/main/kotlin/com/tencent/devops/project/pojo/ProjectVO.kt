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

@ApiModel("项目-显示模型")
data class ProjectVO(
    @ApiModelProperty("主键ID")
    val id: Long,
    @ApiModelProperty("项目ID")
    val project_id: String,
    @ApiModelProperty("项目名称")
    val project_name: String,
    @ApiModelProperty("项目名称")
    val project_code: String,
    @ApiModelProperty("项目类型")
    val project_type: Int,
    @ApiModelProperty("审批状态")
    val approval_status: Int,
    @ApiModelProperty("审批时间")
    val approval_time: String,
    @ApiModelProperty("审批人")
    val approver: String,
    @ApiModelProperty("事业群ID")
    val bg_id: Long,
    @ApiModelProperty("事业群名字")
    val bg_name: String,
    @ApiModelProperty("cc业务ID")
    val cc_app_id: Long,
    @ApiModelProperty("cc业务名称")
    val cc_app_name: String,
    @ApiModelProperty("中心ID")
    val center_id: Long,
    @ApiModelProperty("中心名称")
    val center_name: String,
    @ApiModelProperty("创建时间")
    val created_at: String,
    @ApiModelProperty("创建人")
    val creator: String,
    @ApiModelProperty("数据ID")
    val data_id: Long,
    @ApiModelProperty("部署类型")
    val deploy_type: String,
    @ApiModelProperty("部门ID")
    val dept_id: Long,
    @ApiModelProperty("部门名称")
    val dept_name: String,
    @ApiModelProperty("描述")
    val description: String,
    @ApiModelProperty("英文缩写")
    val english_name: String,
    @ApiModelProperty("extra")
    val extra: String,
    @ApiModelProperty("是否离线")
    @get:JsonProperty("is_offlined")
    val is_offlined: Boolean,
    @ApiModelProperty("是否保密")
    @get:JsonProperty("is_secrecy")
    val is_secrecy: Boolean,
    @ApiModelProperty("是否启用图表激活")
    @get:JsonProperty("is_helm_chart_enabled")
    val is_helm_chart_enabled: Boolean,
    @ApiModelProperty("kind")
    val kind: Int,
    @ApiModelProperty("logo地址")
    val logo_addr: String,
    @ApiModelProperty("评论")
    val remark: String,
    @ApiModelProperty("修改时间")
    val updated_at: String,
    @ApiModelProperty("useBK")
    val use_bk: Boolean,
    @ApiModelProperty("启用")
    val enabled: Boolean,
    @ApiModelProperty("是否灰度")
    val gray: Boolean,
    @ApiModelProperty("是否有权限")
    val permission: Boolean? = true
)
