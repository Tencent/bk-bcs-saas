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

import com.tencent.devops.common.api.exception.PipelineAlreadyExistException
import com.tencent.devops.common.api.pojo.Result
import org.slf4j.LoggerFactory
import javax.ws.rs.core.MediaType
import javax.ws.rs.core.Response
import javax.ws.rs.ext.ExceptionMapper
import javax.ws.rs.ext.Provider

@Provider
class PipelineAlreadyExistExceptionMapper : ExceptionMapper<PipelineAlreadyExistException> {
    companion object {
        val logger = LoggerFactory.getLogger(PipelineAlreadyExistExceptionMapper::class.java)!!
    }

    override fun toResponse(exception: PipelineAlreadyExistException): Response {
        logger.error("Failed with pipeline already exist exception", exception)
        val status = Response.Status.CONFLICT
        val message = "流水线名称已被他人使用"
        return Response.status(status).type(MediaType.APPLICATION_JSON_TYPE).entity(Result<Void>(status.statusCode, message)).build()
    }
}