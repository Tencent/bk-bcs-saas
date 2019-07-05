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
import com.tencent.devops.project.api.UserProjectServiceResource
import com.tencent.devops.project.pojo.Result
import com.tencent.devops.project.pojo.service.ServiceListVO
import com.tencent.devops.project.service.UserProjectSrvService

@RestResource
class UserProjectServiceResourceImpl constructor(private val userProjectSrvService: UserProjectSrvService) :
    UserProjectServiceResource {

    override fun updateCollected(bkToken: String, service_id: Long, collector: Boolean): Result<Boolean> {
        return userProjectSrvService.updateCollected(bkToken, service_id, collector)
    }

    override fun getServiceList(bkToken: String, projectId: String?): Result<List<ServiceListVO>> {
        return userProjectSrvService.listService(bkToken, projectId)
    }
}