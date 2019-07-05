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

package com.tencent.devops.common.service.utils

import org.springframework.beans.BeansException
import org.springframework.context.ApplicationContext
import org.springframework.context.ApplicationContextAware
import org.springframework.stereotype.Component

@Component
class SpringContextUtil : ApplicationContextAware {

    /**
     * 实现ApplicationContextAware接口的回调方法，设置上下文环境
     */
    @Throws(BeansException::class)
    override fun setApplicationContext(applicationContext: ApplicationContext) {
        SpringContextUtil.applicationContext = applicationContext
    }

    companion object {

        // Spring应用上下文环境
        private var applicationContext: ApplicationContext? = null

        /**
         * 获取对象 这里重写了bean方法，起主要作用
         * @param clazz 类名
         * @param <T> Bean
         * @return 实例
         * @throws BeansException 异常
        </T> */
        @Throws(BeansException::class)
        fun <T> getBean(clazz: Class<T>): T {
            return applicationContext!!.getBean(clazz)
        }

        /**
         * 取指定类的指定名称的类的实例对象
         * @param clazz 类名
         * @param beanName 实例对象名称
         * @param <T> Bean
         * @return 实例
         * @throws BeansException 异常
         */
        @Throws(BeansException::class)
        fun <T> getBean(clazz: Class<T>, beanName: String): T {
            return applicationContext!!.getBean(beanName, clazz)
        }

        /**
         * 获取对象列表
         * @param clazz 注解类名
         * @param <T: Annotation> 注解
         * @return 实例列表
         * @throws BeansException 异常
         */
        @Throws(BeansException::class)
        fun <T : Annotation> getBeansWithAnnotation(clazz: Class<T>): List<Any> {
            return applicationContext!!.getBeansWithAnnotation(clazz).values.toList()
        }
    }
}
