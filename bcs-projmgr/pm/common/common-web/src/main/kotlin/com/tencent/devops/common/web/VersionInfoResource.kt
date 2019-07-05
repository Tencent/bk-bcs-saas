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

import io.swagger.annotations.Api
import io.swagger.annotations.ApiOperation
import org.slf4j.LoggerFactory
import javax.ws.rs.Consumes
import javax.ws.rs.GET
import javax.ws.rs.Path
import javax.ws.rs.Produces
import javax.ws.rs.core.MediaType

@RestResource
@Api(tags = ["EXTERNAL_INFO"], description = "获取我们当前的版本信息")
@Path("/external/service/versionInfo")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
class VersionInfoResource {

    @ApiOperation("获取微服务当前信息")
    @GET
    @Path("/")
    fun getInfo(): String {
        try {
            return VersionInfoResource::class.java.getResource("/version.txt").readText()
        } catch (t: Throwable) {
            logger.warn("Fail to read the version info", t)
        }
        return ""
    }

    companion object {
        private val logger = LoggerFactory.getLogger(VersionInfoResource::class.java)
    }
}