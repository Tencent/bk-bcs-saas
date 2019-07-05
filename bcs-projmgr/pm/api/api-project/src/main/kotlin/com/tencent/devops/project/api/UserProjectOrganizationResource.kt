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
import com.tencent.devops.project.pojo.OrganizationInfo
import com.tencent.devops.project.pojo.Result
import com.tencent.devops.project.pojo.enums.OrganizationType
import io.swagger.annotations.Api
import io.swagger.annotations.ApiParam
import javax.ws.rs.Consumes
import javax.ws.rs.GET
import javax.ws.rs.HeaderParam
import javax.ws.rs.Path
import javax.ws.rs.PathParam
import javax.ws.rs.Produces
import javax.ws.rs.core.MediaType

@Api(tags = ["USER_PROJECT_ORGANIZATION"], description = "蓝盾项目列表组织架构接口")
@Path("/user/organizations")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
interface UserProjectOrganizationResource {

    @GET
    @Path("/types/{type}/ids/{id}")
    fun getOrganizations(
        @ApiParam("bk Token", required = true)
        @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
        bkToken: String,
        @ApiParam("bg, 部门或者中心")
        @PathParam("type")
        type: OrganizationType,
        @ApiParam("ID")
        @PathParam("id")
        id: Int
    ): Result<List<OrganizationInfo>>
}