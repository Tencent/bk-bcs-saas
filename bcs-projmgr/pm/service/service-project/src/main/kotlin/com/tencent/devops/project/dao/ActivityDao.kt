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

import com.tencent.devops.model.project.tables.TActivity
import com.tencent.devops.model.project.tables.records.TActivityRecord
import com.tencent.devops.project.pojo.ActivityStatus
import com.tencent.devops.project.pojo.enums.ActivityType
import org.jooq.DSLContext
import org.jooq.Result
import org.springframework.stereotype.Repository

@Repository
class ActivityDao {

    fun list(
        dslContext: DSLContext,
        type: ActivityType,
        status: ActivityStatus
    ): Result<TActivityRecord> {
        with(TActivity.T_ACTIVITY) {
            return dslContext.selectFrom(this)
                .where(TYPE.eq(type.name))
                .orderBy(CREATE_TIME.desc())
                .fetch()
        }
    }
}