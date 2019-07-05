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

@ApiModel("项目信息创建请求实体")
data class OpProjectCreateInfoRequest(
    @JsonProperty(value = "project_id", required = true)
    @ApiModelProperty("项目ID")
    val projectId: String,
    @ApiModelProperty("项目名称")
    @JsonProperty(value = "project_name", required = true)
    val projectName: String,
    @ApiModelProperty("项目英文名称")
    @JsonProperty(value = "english_name", required = true)
    val englishName: String,
    @JsonProperty(value = "creator_bg_name", required = false)
    @ApiModelProperty("注册人所属一级机构")
    val creatorBgName: String?,
    @JsonProperty(value = "creator_dept_name", required = false)
    @ApiModelProperty("注册人所属二级机构")
    val creatorDeptName: String?,
    @JsonProperty(value = "creator_center_name", required = false)
    @ApiModelProperty("注册人所属三级机构")
    val creatorCenterName: String?,
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
    @JsonProperty(value = "project_type", required = true)
    @ApiModelProperty("项目类型")
    val projectType: Int,
    @JsonProperty(value = "approver", required = false)
    @ApiModelProperty("审批人")
    var approver: String?,
    @JsonProperty(value = "approval_status", required = true)
    @ApiModelProperty("审批状态")
    val approvalStatus: Int,
    @JsonProperty(value = "approval_time", required = false)
    @ApiModelProperty("审批时间")
    var approvalTime: Long?,
    @JsonProperty(value = "is_secrecy", required = true)
    @ApiModelProperty("保密性")
    val secrecyFlag: Boolean,
    @JsonProperty(value = "cc_app_id", required = false)
    @ApiModelProperty("应用ID")
    val ccAppId: Long?,
    @JsonProperty(value = "cc_app_name", required = false)
            @ApiModelProperty("应用名称")
            val ccAppName: String?,
    @JsonProperty(value = "kind", required = true)
    @ApiModelProperty("kind")
    val kind: Int,
    @JsonProperty(value = "enabled")
    @ApiModelProperty("启用")
    val enabled: Boolean,
    @JsonProperty(value = "use_bk", required = true)
    @ApiModelProperty("是否用蓝鲸")
    val useBk: Boolean,
    @JsonProperty(value = "labelIdList", required = false)
    @ApiModelProperty("标签id集合")
    val labelIdList: List<String>?
)