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

package com.tencent.devops.common.api.util

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.SerializationFeature
import com.fasterxml.jackson.module.kotlin.KotlinModule

object JsonUtil {
    private val objectMapper = ObjectMapper().apply {
        registerModule(KotlinModule())
        configure(SerializationFeature.INDENT_OUTPUT, true)
        configure(DeserializationFeature.ACCEPT_EMPTY_STRING_AS_NULL_OBJECT, true)
        configure(JsonParser.Feature.ALLOW_UNQUOTED_CONTROL_CHARS, true)
        setSerializationInclusion(JsonInclude.Include.NON_NULL)
        disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
        configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false)
    }

    private val skipEmptyObjectMapper = ObjectMapper().apply {
        registerModule(KotlinModule())
        configure(SerializationFeature.INDENT_OUTPUT, true)
        configure(DeserializationFeature.ACCEPT_EMPTY_STRING_AS_NULL_OBJECT, true)
        configure(JsonParser.Feature.ALLOW_UNQUOTED_CONTROL_CHARS, true)
        setSerializationInclusion(JsonInclude.Include.NON_EMPTY)
        disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
        configure(SerializationFeature.FAIL_ON_EMPTY_BEANS, false)
    }

    fun getObjectMapper() = objectMapper

    /**
     * 转成Json
     */
    fun toJson(bean: Any): String {
        if (ReflectUtil.isNativeType(bean) || bean is String) {
            return bean.toString()
        }
        return getObjectMapper().writeValueAsString(bean)!!
    }

    /**
     * 将对象转可修改的Map,
     * 注意：会忽略掉值为空串和null的属性
     */
    fun toMutableMapSkipEmpty(bean: Any): MutableMap<String, Any> {
        if (ReflectUtil.isNativeType(bean)) {
            return mutableMapOf()
        }
        return if (bean is String)
            skipEmptyObjectMapper.readValue<MutableMap<String, Any>>(
                    bean.toString(),
                    object : TypeReference<MutableMap<String, Any>>() {})
        else
            skipEmptyObjectMapper.readValue<MutableMap<String, Any>>(
                    skipEmptyObjectMapper.writeValueAsString(bean),
                    object : TypeReference<MutableMap<String, Any>>() {})
    }

    /**
     * 将对象转不可修改的Map
     * 注意：会忽略掉值为null的属性
     */
    fun toMap(bean: Any): Map<String, Any> {
        return when {
            ReflectUtil.isNativeType(bean) -> mapOf()
            bean is String -> to(bean)
            else -> to(getObjectMapper().writeValueAsString(bean))
        }
    }

    /**
     * 将json转指定类型对象
     * @param json json字符串
     * @return 指定对象
     */
    fun <T> to(json: String): T {
        return getObjectMapper().readValue<T>(json, object : TypeReference<T>() {})
    }

    fun <T> to(json: String, type: Class<T>): T = getObjectMapper().readValue(json, type)

    fun <T> mapTo(map: Map<String, Any>, type: Class<T>): T = getObjectMapper().readValue(
            getObjectMapper().writeValueAsString(map), type)
}
