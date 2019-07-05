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

package com.tencent.devops.common.web

import com.tencent.devops.common.web.handler.AllExceptionMapper
import com.tencent.devops.common.web.handler.BadRequestExceptionMapper
import com.tencent.devops.common.web.handler.ClientExceptionMapper
import com.tencent.devops.common.web.handler.CodeccReportExceptionMapper
import com.tencent.devops.common.web.handler.CustomExceptionMapper
import com.tencent.devops.common.web.handler.DependNotFoundExceptionMapper
import com.tencent.devops.common.web.handler.IllegalArgumentExceptionMapper
import com.tencent.devops.common.web.handler.JsonMappingExceptionMapper
import com.tencent.devops.common.web.handler.MissingKotlinParameterExceptionMapper
import com.tencent.devops.common.web.handler.NotFoundExceptionMapper
import com.tencent.devops.common.web.handler.OperationExceptionMapper
import com.tencent.devops.common.web.handler.ParamBlankExceptionMapper
import com.tencent.devops.common.web.handler.ParamExceptionMapper
import com.tencent.devops.common.web.handler.PermissionForbiddenExceptionMapper
import com.tencent.devops.common.web.handler.PipelineAlreadyExistExceptionMapper
import com.tencent.devops.common.web.handler.RemoteServiceExceptionMapper
import com.tencent.devops.common.web.handler.RuntimeExceptionMapper
import com.tencent.devops.common.web.handler.UnauthorizedExceptionMapper
import org.glassfish.jersey.media.multipart.MultiPartFeature
import org.glassfish.jersey.server.ResourceConfig
import org.springframework.beans.factory.InitializingBean
import org.springframework.context.ApplicationContext
import org.springframework.context.ApplicationContextAware
import org.springframework.stereotype.Component
import javax.ws.rs.ApplicationPath

@Component
@ApplicationPath("/api")
open class JerseyConfig : ResourceConfig(), ApplicationContextAware, InitializingBean {
    private lateinit var applicationContext: ApplicationContext

    override fun setApplicationContext(applicationContext: ApplicationContext) {
        this.applicationContext = applicationContext
    }

    override fun afterPropertiesSet() {
        register(DependNotFoundExceptionMapper::class.java)
        register(ParamBlankExceptionMapper::class.java)
        register(IllegalArgumentExceptionMapper::class.java)
        register(ParamExceptionMapper::class.java)
        register(MissingKotlinParameterExceptionMapper::class.java)
        register(BadRequestExceptionMapper::class.java)
        register(NotFoundExceptionMapper::class.java)
        register(ClientExceptionMapper::class.java)
        register(RemoteServiceExceptionMapper::class.java)
        register(OperationExceptionMapper::class.java)
        register(UnauthorizedExceptionMapper::class.java)
        register(JsonMappingExceptionMapper::class.java)
        register(RuntimeExceptionMapper::class.java)
        register(AllExceptionMapper::class.java)
        register(MultiPartFeature::class.java)
        register(PipelineAlreadyExistExceptionMapper::class.java)
        register(CustomExceptionMapper::class.java)
        register(PermissionForbiddenExceptionMapper::class.java)
        register(CodeccReportExceptionMapper::class.java)
        val restResources = applicationContext.getBeansWithAnnotation(RestResource::class.java)
        restResources.values.forEach {
            register(it)
        }
        val containerRequestFilter = applicationContext.getBeansWithAnnotation(RequestFilter::class.java)
        containerRequestFilter.values.forEach {
            register(it)
        }
    }
}