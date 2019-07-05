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

import com.tencent.devops.model.project.tables.TFavorite
import com.tencent.devops.model.project.tables.records.TFavoriteRecord
import org.jooq.DSLContext
import org.jooq.Result
import org.springframework.stereotype.Repository

@Repository
class FavoriteDao {

    fun list(dslContext: DSLContext, userId: String): Result<TFavoriteRecord> {
        with(TFavorite.T_FAVORITE) {
            return dslContext.selectFrom(this)
                .where(USERNAME.eq(userId))
                .fetch()
        }
    }

    /**
     * 创建收藏
     */
    fun create(dslContext: DSLContext, userId: String, service_id: Long): Int {
        with(TFavorite.T_FAVORITE) {
            return dslContext.insertInto(this, SERVICE_ID, USERNAME)
                .values(service_id, userId).execute()
        }
    }

    /**
     * 删除收藏
     */
    fun delete(dslContext: DSLContext, userId: String, service_id: Long): Int {
        with(TFavorite.T_FAVORITE) {
            return dslContext.deleteFrom(this)
                .where(SERVICE_ID.eq(service_id))
                .and(USERNAME.eq(userId))
                .execute()
        }
    }
}