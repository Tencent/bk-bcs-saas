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

package com.tencent.devops.project.resources

import com.tencent.devops.common.web.RestResource
import com.tencent.devops.project.api.UserProjectResource
import com.tencent.devops.project.pojo.ProjectCreateInfo
import com.tencent.devops.project.pojo.ProjectUpdateInfo
import com.tencent.devops.project.pojo.ProjectVO
import com.tencent.devops.project.pojo.Result
import com.tencent.devops.project.pojo.enums.ProjectValidateType
import com.tencent.devops.project.service.external.UserProjectService
import org.glassfish.jersey.media.multipart.FormDataContentDisposition
import org.springframework.beans.factory.annotation.Autowired
import java.io.InputStream

@RestResource
class UserProjectResourceImpl @Autowired constructor(
    private val userProjectService: UserProjectService
) : UserProjectResource {

    override fun list(bkToken: String): Result<List<ProjectVO>> {
        return Result(userProjectService.getExternalProjectList(bkToken))
    }

    override fun get(bkToken: String, projectId: String): Result<ProjectVO?> {
        return Result(data = userProjectService.getExternalProject(bkToken, projectId))
    }

    override fun getByCode(bkToken: String, projectCode: String): Result<ProjectVO?> {
        return Result(data = userProjectService.getExternalProjectByCode(bkToken, projectCode))
    }

    override fun listAll(bkToken: String): Result<List<ProjectVO>> {
        return Result(userProjectService.getExternalAllProjectList(bkToken))
    }

    override fun create(bkToken: String, projectCreateInfo: ProjectCreateInfo): Result<Boolean> {
        // 创建蓝盾项目
        userProjectService.create(bkToken ,projectCreateInfo)
        return Result(true)
    }

    override fun update(bkToken: String, projectId: String, projectUpdateInfo: ProjectUpdateInfo): Result<Boolean> {
        userProjectService.update(bkToken, projectId, projectUpdateInfo)
        return Result(true)
    }

    override fun updateLogo(
        bkToken: String,
        projectId: String,
        inputStream: InputStream,
        disposition: FormDataContentDisposition
    ): Result<Boolean> {
        return userProjectService.updateLogo(bkToken, projectId, inputStream, disposition)
    }

    override fun validate(
        bkToken: String,
        validateType: ProjectValidateType,
        name: String,
        project_id: String?
    ): Result<Boolean> {
        userProjectService.validate(bkToken, validateType, name, project_id)
        return Result(true)
    }
}
