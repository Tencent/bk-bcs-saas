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
import com.fasterxml.jackson.module.kotlin.readValue
import com.tencent.devops.common.api.exception.ClientException
import com.tencent.devops.common.api.exception.OperationException
import com.tencent.devops.common.api.exception.RemoteServiceException
import com.tencent.devops.common.api.pojo.Result
import feign.Response
import feign.codec.ErrorDecoder
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import java.io.IOException
import java.lang.Exception

@Service
class ClientErrorDecoder @Autowired constructor(val objectMapper: ObjectMapper) : ErrorDecoder {
    override fun decode(methodKey: String, response: Response): Exception {
        // 首先判断返回结果是否能被序列化
        val responseStream = response.body().asInputStream()
        val result: Result<*>
        try {
            result = objectMapper.readValue(responseStream)
        } catch (e: IOException) {
            return ClientException("内部服务返回结果无法解析")
        }
        if (response.status() == OperationException.statusCode) {
            throw OperationException(result.message ?: "")
        }
        return RemoteServiceException(result.message ?: "", response.status())
    }
}