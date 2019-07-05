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

package com.tencent.devops.common.service

import com.tencent.devops.common.service.gray.Gray
import com.tencent.devops.common.service.utils.SpringContextUtil
import org.springframework.boot.autoconfigure.AutoConfigureBefore
import org.springframework.boot.autoconfigure.AutoConfigureOrder
import org.springframework.cloud.client.discovery.EnableDiscoveryClient
import org.springframework.cloud.consul.ConsulAutoConfiguration
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.PropertySource
import org.springframework.core.Ordered
import org.springframework.core.env.Environment

@Configuration
@PropertySource("classpath:/common-service.properties")
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
@AutoConfigureBefore(ConsulAutoConfiguration::class)
@EnableDiscoveryClient
class ServiceAutoConfiguration {
    @Bean
    fun profile(environment: Environment) = Profile(environment)

    @Bean
    fun springContextUtil() = SpringContextUtil()

    @Bean
    fun gray() = Gray()
}