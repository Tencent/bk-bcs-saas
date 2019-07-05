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

import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.spec.SecretKeySpec
import java.security.SecureRandom
import java.util.Base64

import javax.crypto.Cipher.DECRYPT_MODE
import javax.crypto.Cipher.ENCRYPT_MODE

object SecurityUtil {
    private val UTF8 = "UTF-8"
    private val AES = "AES"
    private val ALGORITHM_PATTERN_COMPLEMENT = "AES/ECB/PKCS5Padding" // 算法/模式/补码方式
    private val secretKeySpec: SecretKeySpec
    private val AES_KEY = "k&nM$3+1"

    init {
        secretKeySpec = generateSecretKeySpec(AES_KEY)
    }

    private fun generateSecretKeySpec(key: String): SecretKeySpec {
        val keyGenerator: KeyGenerator
        val secureRandom: SecureRandom
        try {
            keyGenerator = KeyGenerator.getInstance(AES)
            secureRandom = SecureRandom.getInstance("SHA1PRNG")
            secureRandom.setSeed(key.toByteArray(charset(UTF8)))
        } catch (e: Exception) {
            throw RuntimeException(e.message, e)
        }

        keyGenerator.init(128, secureRandom)
        val secretKey = keyGenerator.generateKey()
        val encoded = secretKey.encoded
        return SecretKeySpec(encoded, AES)
    }

    fun encrypt(content: String): String {
        val cipher = Cipher.getInstance(ALGORITHM_PATTERN_COMPLEMENT)
        cipher.init(ENCRYPT_MODE, secretKeySpec)
        val bytes = cipher.doFinal(content.toByteArray(charset(UTF8)))
        return Base64.getEncoder().encodeToString(bytes)
    }

    fun decrypt(content: String): String {
        val cipher = Cipher.getInstance(ALGORITHM_PATTERN_COMPLEMENT)
        cipher.init(DECRYPT_MODE, secretKeySpec)
        val decode = Base64.getDecoder().decode(content)
        val original = cipher.doFinal(decode)
        return original.toString(kotlin.text.charset(UTF8))
    }

    fun encrypt(key: String, content: String): String {
        val secretKeySpec = generateSecretKeySpec(key)
        val cipher = Cipher.getInstance(ALGORITHM_PATTERN_COMPLEMENT)
        cipher.init(ENCRYPT_MODE, secretKeySpec)
        val bytes = cipher.doFinal(content.toByteArray(charset(UTF8)))
        return Base64.getEncoder().encodeToString(bytes)
    }

    fun decrypt(key: String, content: String): String {
        val secretKeySpec = generateSecretKeySpec(key)
        val cipher = Cipher.getInstance(ALGORITHM_PATTERN_COMPLEMENT)
        cipher.init(DECRYPT_MODE, secretKeySpec)
        val decode = Base64.getDecoder().decode(content)
        val original = cipher.doFinal(decode)
        return original.toString(kotlin.text.charset(UTF8))
    }

    fun encrypt(key: String, content: ByteArray): ByteArray {
        val secretKeySpec = generateSecretKeySpec(key)
        val cipher = Cipher.getInstance(ALGORITHM_PATTERN_COMPLEMENT)
        cipher.init(ENCRYPT_MODE, secretKeySpec)
        return cipher.doFinal(content)
    }

    fun decrypt(key: String, content: ByteArray): ByteArray {
        val secretKeySpec = generateSecretKeySpec(key)
        val cipher = Cipher.getInstance(ALGORITHM_PATTERN_COMPLEMENT)
        cipher.init(DECRYPT_MODE, secretKeySpec)
        return cipher.doFinal(content)
    }
}

fun main(argv: Array<String>) {
    println(SecurityUtil.decrypt("Ln1UX8DJZm/SUzJHNpAVng/wHBP7H8KiWOlufXGiosA="))
}