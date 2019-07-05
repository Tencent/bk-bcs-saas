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
import java.util.Random

object ApiUtil {
    private val HASH_SALT = "soda3:com.tencent.soda.open.api.access.key.salt"
    private val hashids = Hashids(HASH_SALT, 8, "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789")
    private val secretSeed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    fun accessKey(projectId: Long): String {
        return hashids.encode(projectId)
    }

    fun randomSecretKey(): String {
        val random = Random()
        val buf = StringBuffer()
        for (i in 0 until 31) {
            val num = random.nextInt(secretSeed.length)
            buf.append(secretSeed[num])
        }
        return buf.toString()
    }
}