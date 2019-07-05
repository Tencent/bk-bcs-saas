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

@ApiModel("项目信息响应信息体")
data class ProjectInfoResponse(
    @JsonProperty(value = "project_id", required = true)
    @ApiModelProperty("项目ID")
    val projectId: String,
    @ApiModelProperty("项目名称")
    @JsonProperty(value = "project_name", required = true)
    val projectName: String,
    @JsonProperty(value = "english_name", required = true)
    @ApiModelProperty("项目英文简称")
    val projectEnglishName: String,
    @JsonProperty(value = "creator_bg_name", required = true)
    @ApiModelProperty("注册人所属一级机构")
    val creatorBgName: String,
    @JsonProperty(value = "creator_dept_name", required = true)
    @ApiModelProperty("注册人所属二级机构")
    val creatorDeptName: String,
    @JsonProperty(value = "creator_center_name", required = true)
    @ApiModelProperty("注册人所属三级机构")
    val creatorCenterName: String,
    @JsonProperty(value = "bg_id", required = true)
    @ApiModelProperty("项目所属一级机构ID")
    val bgId: Long,
    @JsonProperty(value = "bg_name", required = true)
    @ApiModelProperty("项目所属一级机构名称")
    val bgName: String,
    @JsonProperty(value = "dept_id", required = true)
    @ApiModelProperty("项目所属二级机构ID")
    val deptId: Long,
    @JsonProperty(value = "dept_name", required = true)
    @ApiModelProperty("项目所属二级机构名称")
    val deptName: String,
    @JsonProperty(value = "center_id", required = true)
    @ApiModelProperty("项目所属三级机构ID")
    val centerId: Long,
    @JsonProperty(value = "center_name", required = true)
    @ApiModelProperty("项目所属三级机构名称")
    val centerName: String,
    @JsonProperty(value = "project_type", required = false)
    @ApiModelProperty("项目类型")
    val projectType: Int?,
    @JsonProperty(value = "approver", required = false)
    @ApiModelProperty("审批人")
    val approver: String?,
    @JsonProperty(value = "approval_time", required = false)
    @ApiModelProperty("审批时间")
    val approvalTime: Long?,
    @JsonProperty(value = "approval_status", required = true)
    @ApiModelProperty("审批状态")
    val approvalStatus: Int,
    @JsonProperty(value = "is_secrecy", required = true)
    @ApiModelProperty("保密性")
    val secrecyFlag: Boolean,
    @JsonProperty(value = "creator", required = true)
    @ApiModelProperty("创建人")
    val creator: String,
    @JsonProperty(value = "created_at", required = true)
    @ApiModelProperty("注册时间")
    val createdAtTime: Long,
    @JsonProperty(value = "cc_app_id", required = false)
    @ApiModelProperty("应用ID")
    val ccAppId: Long?,
    @JsonProperty(value = "cc_app_name", required = false)
    @ApiModelProperty("cc业务名称")
    val ccAppName: String?,
    @JsonProperty(value = "use_bk", required = false)
    @ApiModelProperty("是否用蓝鲸")
    val useBk: Boolean?,
    @JsonProperty(value = "is_offlined", required = false)
    @ApiModelProperty("是否停用")
    val offlinedFlag: Boolean?,
    @JsonProperty(value = "kind", required = true)
    @ApiModelProperty("kind")
    val kind: Int,
    @JsonProperty(value = "enabled", required = true)
    @ApiModelProperty("启用")
    val enabled: Boolean,
    @JsonProperty(value = "is_gray", required = true)
    @ApiModelProperty("是否灰度 true：是 false：否")
    val grayFlag: Boolean
)
