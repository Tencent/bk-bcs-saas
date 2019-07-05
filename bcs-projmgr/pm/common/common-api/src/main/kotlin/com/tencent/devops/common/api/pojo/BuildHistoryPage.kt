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

package com.tencent.devops.common.api.pojo

import io.swagger.annotations.ApiModel
import io.swagger.annotations.ApiModelProperty

@ApiModel("构建历史-分页数据包装模型")
data class BuildHistoryPage<out T>(
    @ApiModelProperty("总记录行数", required = true)
    val count: Long,
    @ApiModelProperty("第几页", required = true)
    val page: Int,
    @ApiModelProperty("每页多少条", required = true)
    val pageSize: Int,
    @ApiModelProperty("总共多少页", required = true)
    val totalPages: Int,
    @ApiModelProperty("数据", required = true)
    val records: List<T>,
    @ApiModelProperty("是否拥有下载构建的权限", required = true)
    val hasDownloadPermission: Boolean,
    @ApiModelProperty("最新的编排版本号", required = true)
    val pipelineVersion: Int
) {
    constructor(page: Int, pageSize: Int, count: Long, records: List<T>, hasDownloadPermission: Boolean, pipelineVersion: Int) :
            this(count, page, pageSize, Math.ceil(count * 1.0 / pageSize).toInt(), records, hasDownloadPermission, pipelineVersion)
}
