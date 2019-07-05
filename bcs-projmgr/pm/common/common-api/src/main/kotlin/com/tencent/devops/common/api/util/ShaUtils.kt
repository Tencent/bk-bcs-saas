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

import org.bouncycastle.util.encoders.Hex
import org.jetbrains.kotlin.daemon.common.toHexString
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

object ShaUtils {

    fun sha1(str: ByteArray): String {
        // 指定sha1算法
        val digest = MessageDigest.getInstance("SHA-1")
        digest.update(str)
        // 获取字节数组
        val messageDigest = digest.digest()

        // 字节数组转换为 十六进制 数
        return messageDigest.toHexString()
    }

    fun hmacSha1(key: ByteArray, data: ByteArray): String {
        val secretKey = SecretKeySpec(key, "HmacSHA1")
        val mac = Mac.getInstance("HmacSHA1")
        mac.init(secretKey)
        val messageDigest = mac.doFinal(data)

        // 字节数组转换为 十六进制 数
        return messageDigest.toHexString()
    }

    fun isEqual(shaA: String, shaB: String): Boolean {
        return isEqual(Hex.decode(shaA), Hex.decode(shaB))
    }

    fun isEqual(shaA: ByteArray, shaB: ByteArray): Boolean {
        return MessageDigest.isEqual(shaA, shaB)
    }
}