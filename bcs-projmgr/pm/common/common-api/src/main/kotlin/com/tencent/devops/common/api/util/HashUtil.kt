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

import org.hashids.Hashids

object HashUtil {
    private val HASH_SALT = "jhy^3(@So0"
    private val hashids = Hashids(HASH_SALT, 8, "abcdefghijklmnopqrstuvwxyz")

    // 新增其他数据类型的HASH_ID实例，防止被爆破后相同盐值破解PROJECT_ID
    private val OTHER_HASH_SALT = "xlm&gst@Fami1y"
    private val otherHashIds = Hashids(OTHER_HASH_SALT, 4)

    fun encodeLongId(id: Long): String {
        return hashids.encode(id)
    }

    fun encodeIntId(id: Int): String {
        return hashids.encode(id.toLong())
    }

    fun decodeIdToLong(hash: String): Long {
        val ids = hashids.decode(hash)
        return if (ids == null || ids.isEmpty()) {
            0L
        } else {
            ids[0]
        }
    }

    fun decodeIdToInt(hash: String): Int {
        val ids = hashids.decode(hash)
        return if (ids == null || ids.isEmpty()) {
            0
        } else {
            ids[0].toInt()
        }
    }

    fun encodeOtherLongId(id: Long): String {
        return otherHashIds.encode(id)
    }

    fun encodeOtherIntId(id: Int): String {
        return otherHashIds.encode(id.toLong())
    }

    fun decodeOtherIdToLong(hash: String): Long {
        val ids = otherHashIds.decode(hash)
        return if (ids == null || ids.isEmpty()) {
            0L
        } else {
            ids[0]
        }
    }

    fun decodeOtherIdToInt(hash: String): Int {
        val ids = otherHashIds.decode(hash)
        return if (ids == null || ids.isEmpty()) {
            0
        } else {
            ids[0].toInt()
        }
    }
}

fun main(args: Array<String>) {
    println(HashUtil.decodeIdToLong("qjpbkdem"))
}