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

package com.tencent.devops.project.api.pojo

import com.fasterxml.jackson.annotation.JsonProperty

data class XBkAuthResourceModifyRequest(
        @JsonProperty("resource_id")
        val resourceId: Set<ResourceId?>?,
        @JsonProperty("resource_name")
        val resourceName: String?, // 2019.4.1测试资源修改
        @JsonProperty("resource_type")
        val resourceType: String?, // env_node
        @JsonProperty("scope_id")
        val scopeId: String?, // projecttest01
        @JsonProperty("scope_type")
        val scopeType: String? // project
) {
    data class ResourceId(
            @JsonProperty("resource_id")
            val resourceId: String?, // ccc
            @JsonProperty("resource_type")
            val resourceType: String? // env_node
    )
}