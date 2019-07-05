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

package com.tencent.devops.project.api

import org.springframework.stereotype.Component

@Component
data class XBkAuthProperties(
    val envName: String? = null,
    val idProvider: String? = null,
    val grantType: String? = null,
    val url: String? = null,
    val bcsSecret: String? = null,
    val codeSecret: String? = null,
    val pipelineSecret: String? = null,
    val artifactorySecret: String? = null,
    val ticketSecret: String? = null,
    val environmentSecret: String? = null,
    val experienceSecret: String? = null,
    val thirdPartyAgentSecret: String? = null,
    val vsSecret: String? = null,
    val qualitySecret: String? = null
)