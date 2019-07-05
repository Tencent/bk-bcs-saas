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

package com.tencent.devops.project.dao

import com.tencent.devops.model.project.tables.TGrayTest
import com.tencent.devops.project.pojo.service.GrayTestInfo
import org.jooq.DSLContext
import org.springframework.stereotype.Repository

@Repository
class GrayTestDao {

    fun listByUser(dslContext: DSLContext, userId: String): List<GrayTestInfo> {
        with(TGrayTest.T_GRAY_TEST) {
            return dslContext.selectFrom(this)
                .where(USERNAME.eq(userId))
                .orderBy(ID.desc())
                .fetch {
                    GrayTestInfo(it.id, it.serviceId, it.username, it.status)
                }
        }
    }
}