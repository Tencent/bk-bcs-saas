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

package com.tencent.devops.common.web.handler

import com.tencent.devops.common.api.exception.CustomException
import com.tencent.devops.common.api.pojo.Result
import org.slf4j.LoggerFactory
import javax.ws.rs.core.MediaType
import javax.ws.rs.core.Response
import javax.ws.rs.ext.ExceptionMapper
import javax.ws.rs.ext.Provider

@Provider
class CustomExceptionMapper : ExceptionMapper<CustomException> {
    companion object {
        val logger = LoggerFactory.getLogger(CustomExceptionMapper::class.java)!!
    }

    override fun toResponse(exception: CustomException): Response {
        logger.error("Failed with custom exception", exception)
        return Response.status(exception.status)
                .type(MediaType.APPLICATION_JSON_TYPE)
                .entity(Result<Void>(exception.status.statusCode, exception.message ?: "Internal Exception")).build()
    }
}