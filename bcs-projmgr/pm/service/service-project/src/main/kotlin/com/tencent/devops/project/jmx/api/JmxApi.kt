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

package com.tencent.devops.project.jmx.api

import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.jmx.export.MBeanExporter
import org.springframework.stereotype.Component
import javax.management.ObjectName

@Component
class JmxApi @Autowired constructor(private val mBeanExporter: MBeanExporter) {

    private val apis = HashMap<String, APIPerformanceBean>()

    fun execute(api: String, elapse: Long, success: Boolean) {
        try {
            getBean(api).execute(elapse, success)
        } catch (t: Throwable) {
            logger.warn("Fail to record the api performance of api $api", t)
        }
    }

    private fun getBean(api: String): APIPerformanceBean {
        var bean = apis[api]
        if (bean == null) {
            synchronized(this) {
                bean = apis[api]
                if (bean == null) {
                    bean = APIPerformanceBean()
                    val name = "com.tencent.devops.project:type=apiPerformance,name=$api"
                    logger.info("Register $api api performance mbean")
                    mBeanExporter.registerManagedResource(bean, ObjectName(name))
                    apis[api] = bean!!
                }
            }
        }
        return bean!!
    }

    companion object {
        private val logger = LoggerFactory.getLogger(JmxApi::class.java)

        const val PROJECT_LIST = "project_list"
        const val PROJECT_CREATE = "project_create"
        const val PROJECT_UPDATE = "project_update"
    }
}
