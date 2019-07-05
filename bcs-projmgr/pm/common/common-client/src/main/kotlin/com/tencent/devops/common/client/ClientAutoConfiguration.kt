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

package com.tencent.devops.common.client

import com.fasterxml.jackson.databind.ObjectMapper
import com.tencent.devops.common.client.pojo.AllProperties
import com.tencent.devops.common.client.pojo.EnvProperties
import com.tencent.devops.common.service.ServiceAutoConfiguration
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.autoconfigure.AutoConfigureAfter
import org.springframework.boot.autoconfigure.AutoConfigureOrder
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean
import org.springframework.cloud.client.loadbalancer.LoadBalancerAutoConfiguration
import org.springframework.cloud.consul.discovery.ConsulDiscoveryClient
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Profile
import org.springframework.context.annotation.PropertySource
import org.springframework.core.Ordered

@Configuration
@PropertySource("classpath:/common-client.properties")
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
@AutoConfigureAfter(ServiceAutoConfiguration::class, LoadBalancerAutoConfiguration::class)
class ClientAutoConfiguration {

    @Bean
    fun allProperties() = AllProperties()

    @Bean
    @Profile("prod")
    fun prodProperties(allProperties: AllProperties) = EnvProperties(allProperties.gatewayProdUrl)

    @Bean
    @Profile("test")
    fun testProperties(allProperties: AllProperties) = EnvProperties(allProperties.gatewayTestUrl)

    @Bean
    @Profile("dev", "default")
    fun devProperties(allProperties: AllProperties) = EnvProperties(allProperties.gatewayDevUrl)

    @Bean
    fun clientErrorDecoder(objectMapper: ObjectMapper) = ClientErrorDecoder(objectMapper)

    @Bean
    @ConditionalOnMissingBean(Client::class)
    fun client(
        clientErrorDecoder: ClientErrorDecoder,
        envProperties: EnvProperties,
        objectMapper: ObjectMapper,
        @Autowired(required = false) consulDiscoveryClient: ConsulDiscoveryClient?
    ) = Client(consulDiscoveryClient, clientErrorDecoder, envProperties, objectMapper)
}
