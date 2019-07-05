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

package com.tencent.devops.common.client.pojo

import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component

@Component
class AllProperties {
    @Value("\${gateway.dev.url:#{null}}")
    val gatewayDevUrl: String? = null
    @Value("\${gateway.test.url:#{null}}")
    val gatewayTestUrl: String? = null
    @Value("\${gateway.prod.url:#{null}}")
    val gatewayProdUrl: String? = null
}