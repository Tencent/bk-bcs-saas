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

package com.tencent.devops.common.web

import com.tencent.devops.common.api.util.JsonUtil
import com.tencent.devops.common.web.jasypt.DefaultEncryptor
import org.springframework.boot.autoconfigure.AutoConfigureBefore
import org.springframework.boot.autoconfigure.AutoConfigureOrder
import org.springframework.boot.autoconfigure.condition.ConditionalOnWebApplication
import org.springframework.boot.autoconfigure.jersey.JerseyAutoConfiguration
import org.springframework.boot.autoconfigure.jmx.JmxAutoConfiguration
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Primary
import org.springframework.context.annotation.Profile
import org.springframework.context.annotation.PropertySource
import org.springframework.core.Ordered

@Configuration
@PropertySource("classpath:/common-web.properties")
@ConditionalOnWebApplication
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
@AutoConfigureBefore(JerseyAutoConfiguration::class)
@EnableConfigurationProperties(SwaggerProperties::class)
class WebAutoConfiguration {

    @Bean
    @Profile("prod")
    fun jerseyConfig() = JerseyConfig()

    @Bean
    @Profile("!prod")
    fun jerseySwaggerConfig() = JerseySwaggerConfig()

    @Bean
    @Primary
    fun objectMapper() = JsonUtil.getObjectMapper()

    @Bean("jasyptStringEncryptor")
    @Primary
    fun stringEncryptor() = DefaultEncryptor()

    @Bean
    fun versionInfoResource() = VersionInfoResource()

    @Bean
    fun jmxAutoConfiguration() = JmxAutoConfiguration()
}