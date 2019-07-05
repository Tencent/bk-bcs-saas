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

import org.bouncycastle.crypto.engines.AESEngine
import org.bouncycastle.crypto.modes.CBCBlockCipher
import org.bouncycastle.crypto.paddings.PKCS7Padding
import org.bouncycastle.crypto.paddings.PaddedBufferedBlockCipher
import org.bouncycastle.crypto.params.KeyParameter
import org.bouncycastle.jce.provider.BouncyCastleProvider
import java.security.SecureRandom
import java.security.Security
import java.util.Arrays
import java.util.Base64
import javax.crypto.KeyGenerator

object AESUtil {
    private val UTF8 = "UTF-8"
    private val AES = "AES"

    init {
        Security.addProvider(BouncyCastleProvider())
    }

    private fun generateKeyParameter(key: String): KeyParameter {
        val keyGenerator: KeyGenerator
        val secureRandom: SecureRandom
        try {
            keyGenerator = KeyGenerator.getInstance(AES)
            secureRandom = SecureRandom.getInstance("SHA1PRNG")
            secureRandom.setSeed(key.toByteArray(charset(UTF8)))
        } catch (e: Exception) {
            throw RuntimeException(e.message, e)
        }

        keyGenerator.init(256, secureRandom)
        val secretKey = keyGenerator.generateKey()
        val encoded = secretKey.encoded
        return KeyParameter(encoded)
    }

    private fun processData(encrypt: Boolean, keyParameter: KeyParameter, bytes: ByteArray): ByteArray
    {
        val blockCipherPadding = PKCS7Padding()
        val blockCipher = CBCBlockCipher(AESEngine())
        val paddedBufferedBlockCipher = PaddedBufferedBlockCipher(blockCipher, blockCipherPadding)
        paddedBufferedBlockCipher.init(encrypt, keyParameter)

        val output = ByteArray(paddedBufferedBlockCipher.getOutputSize(bytes.size))
        val offset = paddedBufferedBlockCipher.processBytes(bytes, 0, bytes.size, output, 0)
        val outputLength = paddedBufferedBlockCipher.doFinal(output, offset)
        return Arrays.copyOf(output, offset + outputLength)
    }

    fun encrypt(key: String, content: String): String {
        val bytes = content.toByteArray(charset(UTF8))
        val keyParameter = generateKeyParameter(key)
        val output = processData(true, keyParameter, bytes)
        return Base64.getEncoder().encodeToString(output)
    }

    fun decrypt(key: String, content: String): String {
        val bytes = Base64.getDecoder().decode(content)
        val keyParameter = generateKeyParameter(key)
        val output = processData(false, keyParameter, bytes)
        return output.toString(charset(UTF8))
    }

    fun encrypt(key: String, content: ByteArray): ByteArray {
        val keyParameter = generateKeyParameter(key)
        return processData(true, keyParameter, content)
    }

    fun decrypt(key: String, content: ByteArray): ByteArray {
        val keyParameter = generateKeyParameter(key)
        return processData(false, keyParameter, content)
    }
}

fun main(argv: Array<String>) {
    val str = "123456789012345678901234567123456789012345"
    val encrypted = AESUtil.encrypt("1234567890abcdef1234567890abcdef", str)
    val decrpted = AESUtil.decrypt("1234567890abcdef1234567890abcdef", encrypted)
    println(decrpted)
}