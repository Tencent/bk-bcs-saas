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

package com.tencent.devops.common.api.util

import com.tencent.devops.common.api.model.SQLLimit

object PageUtil {
    fun convertPageSizeToSQLLimit(page: Int, pageSize: Int): SQLLimit {
        val oneOffsetPage = if (page <= 0) 1 else page
        val defaultPageSize = if (pageSize <= 0) 10 else pageSize
        return SQLLimit((oneOffsetPage - 1) * defaultPageSize, defaultPageSize)
    }

    // page & pageSize为空则不分页
    fun convertPageSizeToSQLLimit(page: Int?, pageSize: Int?): SQLLimit {
        val oneOffsetPage = if (page == null || page <= 0) 1 else page
        val defaultPageSize = if (pageSize == null || pageSize <= 0) -1 else pageSize
        return SQLLimit((oneOffsetPage - 1) * defaultPageSize, defaultPageSize)
    }
}