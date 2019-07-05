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

package com.tencent.devops.common.api.param

import com.fasterxml.jackson.annotation.JsonProperty

interface ReqParam {

    fun beanToMap(): Map<String, String> {
        val result = mutableMapOf<String, String>()

        var aClass: Class<*>? = this.javaClass
        while (aClass != null) {
            val declaredFields = aClass.declaredFields
            for (field in declaredFields) {
                val key: String
                val annotation = field.getDeclaredAnnotation(JsonProperty::class.java)
                key = annotation?.value ?: field.name
                if (!field.isAccessible) {
                    field.isAccessible = true
                    try {
                        val b = field.get(this)
                        if (b != null && b != "") {
                            result[key] = b.toString()
                        }
                    } catch (ignored: IllegalAccessException) {
                    } finally {
                        field.isAccessible = false
                    }
                }
            }
            aClass = aClass.superclass
        }
        return result
    }
}