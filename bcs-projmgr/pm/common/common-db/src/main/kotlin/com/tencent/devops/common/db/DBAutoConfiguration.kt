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

package com.tencent.devops.common.db

import com.mysql.jdbc.Driver
import com.zaxxer.hikari.HikariDataSource
import org.springframework.beans.factory.annotation.Value
import org.springframework.boot.autoconfigure.AutoConfigureBefore
import org.springframework.boot.autoconfigure.AutoConfigureOrder
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
import org.springframework.boot.autoconfigure.jooq.JooqAutoConfiguration
import org.springframework.context.annotation.Configuration
import org.springframework.core.Ordered
import org.springframework.context.annotation.Primary
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.PropertySource
import org.springframework.transaction.annotation.EnableTransactionManagement
import javax.sql.DataSource

@Configuration
@PropertySource("classpath:/common-db.properties")
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
@AutoConfigureBefore(DataSourceAutoConfiguration::class, JooqAutoConfiguration::class)
@EnableTransactionManagement
class DBAutoConfiguration {

    @Value("\${spring.datasource.url:#{null}}")
    private val datasourceUrl: String? = null
    @Value("\${spring.datasource.username:#{null}}")
    private val datasourceUsername: String? = null
    @Value("\${spring.datasource.password:#{null}}")
    private val datasourcePassword: String? = null

    @Bean
    @Primary
    fun dataSource(): DataSource {
        if (datasourceUrl == null || datasourceUrl!!.isBlank()) {
            throw IllegalArgumentException("Database connection address is not configured")
        }
        return HikariDataSource().apply {
            poolName = "DBPool-Main"
            jdbcUrl = datasourceUrl
            username = datasourceUsername
            password = datasourcePassword
            driverClassName = Driver::class.java.name
            minimumIdle = 10
            maximumPoolSize = 50
            idleTimeout = 60000
        }
    }
}