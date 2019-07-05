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
import com.tencent.devops.project.pojo.Result
import com.tencent.devops.project.pojo.ProjectCreateInfo
import com.tencent.devops.project.pojo.ProjectUpdateInfo
import com.tencent.devops.project.pojo.ProjectVO
import com.tencent.devops.project.pojo.enums.ProjectValidateType
import io.swagger.annotations.Api
import io.swagger.annotations.ApiOperation
import io.swagger.annotations.ApiParam
import org.glassfish.jersey.media.multipart.FormDataContentDisposition
import org.glassfish.jersey.media.multipart.FormDataParam
import java.io.InputStream
import javax.ws.rs.Consumes
import javax.ws.rs.GET
import javax.ws.rs.HeaderParam
import javax.ws.rs.POST
import javax.ws.rs.PUT
import javax.ws.rs.Path
import javax.ws.rs.PathParam
import javax.ws.rs.Produces
import javax.ws.rs.QueryParam
import javax.ws.rs.core.MediaType

@Api(tags = ["USER_PROJECT"], description = "蓝盾项目列表接口")
@Path("/user/projects")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
interface UserProjectResource {

    @GET
    @Path("/")
    @ApiOperation("查询用户所有项目")
    fun list(
            @ApiParam("bk Token", required = true)
            @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
            bkToken: String
    ): Result<List<ProjectVO>>

    @GET
    @Path("/{project_id}")
    @ApiOperation("查询项目信息")
    fun get(
            @ApiParam("bk Token", required = true)
            @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
            bkToken: String,
            @ApiParam("项目id", required = true)
            @PathParam("project_id")
            projectId: String
    ): Result<ProjectVO?>

    @GET
    @Path("/getProjectByCode/{project_code}")
    @ApiOperation("查询项目信息")
    fun getByCode(
            @ApiParam("bk Token", required = true)
            @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
            bkToken: String,
            @ApiParam("项目code", required = true)
            @PathParam("project_code")
            projectCode: String
    ): Result<ProjectVO?>

    @GET
    @Path("/listAll")
    @ApiOperation("列出所有项目简单信息")
    fun listAll(
            @ApiParam("bk Token", required = true)
            @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
            bkToken: String
    ): Result<List<ProjectVO>>

    @POST
    @Path("/")
    @ApiOperation("创建项目")
    fun create(
            @ApiParam("bk Token", required = true)
            @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
            bkToken: String,
            @ApiParam(value = "项目信息", required = true)
            projectCreateInfo: ProjectCreateInfo
    ): Result<Boolean>

    @PUT
    @Path("/{project_id}")
    @ApiOperation("修改项目")
    fun update(
            @ApiParam("bk Token", required = true)
            @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
            bkToken: String,
            @ApiParam("项目ID", required = true)
            @PathParam("project_id")
            projectId: String,
            @ApiParam(value = "项目信息", required = true)
            projectUpdateInfo: ProjectUpdateInfo
    ): Result<Boolean>

    @PUT
    @Path("/{project_id}/logo")
    @ApiOperation("更改项目logo")
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    fun updateLogo(
            @ApiParam("bk Token", required = true)
            @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
            bkToken: String,
            @ApiParam("项目ID", required = true)
            @PathParam("project_id")
            projectId: String,
            @ApiParam("文件", required = true)
            @FormDataParam("logo")
            inputStream: InputStream,
            @FormDataParam("logo")
            disposition: FormDataContentDisposition
    ): Result<Boolean>

    @PUT
    @Path("/{validateType}/names/{name}/validate")
    @ApiOperation("校验项目名称和项目英文名")
    fun validate(
            @ApiParam("bk Token", required = true)
            @HeaderParam(AUTH_HEADER_DEVOPS_BK_TOKEN)
            bkToken: String,
            @ApiParam("校验的是项目名称或者项目英文名")
            @PathParam("validateType")
            validateType: ProjectValidateType,
            @ApiParam("项目名称或者项目英文名")
            @PathParam("name")
            name: String,
            @ApiParam("项目ID")
            @QueryParam("project_id")
            project_id: String?
    ): Result<Boolean>
}