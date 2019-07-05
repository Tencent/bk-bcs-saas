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

package com.tencent.devops.project.api

import com.tencent.devops.common.api.auth.AUTH_HEADER_DEVOPS_BK_TOKEN
import com.tencent.devops.common.api.auth.AUTH_HEADER_DEVOPS_PROJECT_ID
import com.tencent.devops.project.pojo.Result
import com.tencent.devops.project.pojo.service.ServiceListVO
import io.swagger.annotations.Api
import io.swagger.annotations.ApiOperation
import io.swagger.annotations.ApiParam
import javax.ws.rs.Consumes
import javax.ws.rs.GET
import javax.ws.rs.HeaderParam
import javax.ws.rs.PUT
import javax.ws.rs.Path
import javax.ws.rs.PathParam
import javax.ws.rs.Produces
import javax.ws.rs.QueryParam
import javax.ws.rs.core.MediaType

@Api(tags = ["USER_PROJECT_SERVICE"], description = "蓝盾项目服务管理接口")
@Path("/user")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
interface UserProjectServiceResource {

    @GET
    @Path("/services")
    @ApiOperation("查询所有服务")
    fun getServiceList(
        @ApiParam("bk Token", required = true)
        @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
        bkToken: String,
        @ApiParam("项目ID", required = false)
        @HeaderParam(AUTH_HEADER_DEVOPS_PROJECT_ID)
        projectId: String?
    ): Result<List<ServiceListVO>>

    @PUT
    @Path("/services/{service_id}")
    @ApiOperation("用户修改关注")
    fun updateCollected(
        @ApiParam("bk Token", required = true)
        @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
        bkToken: String,
        @ApiParam("服务ID")
        @PathParam("service_id")
        service_id: Long,
        @ApiParam("关注/取消关注")
        @QueryParam("collector")
        collector: Boolean
    ): Result<Boolean>
}