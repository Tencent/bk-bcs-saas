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

package com.tencent.devops.common.web.jmx.exception

import com.tencent.devops.common.service.Profile
import com.tencent.devops.common.service.utils.SpringContextUtil
import org.slf4j.LoggerFactory
import org.springframework.jmx.export.MBeanExporter
import javax.management.ObjectName

object JmxExceptions {

    private val exceptions = HashMap<String/*exceptionName*/, ExceptionBean>()

    fun encounter(exception: Throwable) {
        try {
            val bean = getBean(exception) ?: return
            bean.incre()
        } catch (t: Throwable) {
            logger.warn("Fail to record the exception ${exception.message}", t)
        }
    }

    private fun getBean(t: Throwable): ExceptionBean? {
        val className = t.javaClass.name
        var bean = exceptions[className]
        if (bean == null) {
            synchronized(this) {
                bean = exceptions[className]
                if (bean == null) {
                    bean = ExceptionBean(className)
                    val serviceName = SpringContextUtil.getBean(Profile::class.java).getApplicationName()
                    if (serviceName.isNullOrBlank()) {
                        logger.warn("Fail to get the service name, ignore the mbean")
                        return null
                    }
                    val name = "com.tencent.devops.$serviceName:type=exceptions,name=$className"
                    logger.info("Register exception $className mbean")
                    SpringContextUtil.getBean(MBeanExporter::class.java).registerManagedResource(bean, ObjectName(name))
                    exceptions.put(className, bean!!)
                }
            }
        }
        return bean
    }

    private val logger = LoggerFactory.getLogger(JmxExceptions::class.java)
}

fun main(argv: Array<String>) {
    val throwable = Throwable("sss")
    println(throwable.javaClass.name)
}