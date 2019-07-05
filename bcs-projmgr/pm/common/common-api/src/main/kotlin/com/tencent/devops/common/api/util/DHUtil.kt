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

import org.bouncycastle.jce.provider.BouncyCastleProvider
import java.security.KeyFactory
import java.security.KeyPairGenerator
import java.security.Security
import java.security.spec.X509EncodedKeySpec
import javax.crypto.interfaces.DHPublicKey
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec
import javax.crypto.KeyAgreement
import java.security.spec.PKCS8EncodedKeySpec
import java.math.BigInteger
import java.security.SecureRandom
import javax.crypto.spec.DHParameterSpec


object DHUtil {
    private val KEY_ALGORITHM = "DH"
    private val KEY_PROVIDER = "BC"
    private val SECRECT_ALGORITHM = "DES"
    // private val KEY_SIZE = 1024
    private val p = BigInteger("16560215747140417249215968347342080587", 16)
    private val g = BigInteger("1234567890", 16)

    init {
        Security.addProvider(BouncyCastleProvider())
    }

    fun initKey(): DHKeyPair {
        val keyPairGenerator = KeyPairGenerator.getInstance(KEY_ALGORITHM, KEY_PROVIDER)
        val serverParam = DHParameterSpec(p, g, 128)
        keyPairGenerator.initialize(serverParam, SecureRandom())
        // keyPairGenerator.initialize(KEY_SIZE)
        val keyPair = keyPairGenerator.generateKeyPair()
        return DHKeyPair(keyPair.public.encoded, keyPair.private.encoded)
    }

    fun initKey(partyAPublicKey: ByteArray): DHKeyPair {
        val x509KeySpec = X509EncodedKeySpec(partyAPublicKey)
        val keyFactory = KeyFactory.getInstance(KEY_ALGORITHM)
        val publicKey = keyFactory.generatePublic(x509KeySpec)

        val dhParameterSpec = (publicKey as DHPublicKey).params
        val keyPairGenerator = KeyPairGenerator.getInstance(KEY_ALGORITHM, KEY_PROVIDER)
        keyPairGenerator.initialize(dhParameterSpec)
        // keyPairGenerator.initialize(KEY_SIZE)
        val keyPair = keyPairGenerator.genKeyPair()
        return DHKeyPair(keyPair.public.encoded, keyPair.private.encoded)
    }

    fun encrypt(data: ByteArray, partAPublicKey: ByteArray, partBPrivateKey: ByteArray): ByteArray {
        val key = getSecretKey(partAPublicKey, partBPrivateKey)
        val secretKey = SecretKeySpec(key, SECRECT_ALGORITHM)
        val cipher = Cipher.getInstance(secretKey.algorithm)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        return cipher.doFinal(data)
    }

    fun decrypt(data: ByteArray, partBPublicKey: ByteArray, partAPrivateKey: ByteArray): ByteArray {
        val key = getSecretKey(partBPublicKey, partAPrivateKey)
        val secretKey = SecretKeySpec(key, SECRECT_ALGORITHM)
        val cipher = Cipher.getInstance(secretKey.algorithm)
        cipher.init(Cipher.DECRYPT_MODE, secretKey)
        return cipher.doFinal(data)
    }

    private fun getSecretKey(publicKey: ByteArray, privateKey: ByteArray): ByteArray {
        // 实例化密钥工厂
        val keyFactory = KeyFactory.getInstance(KEY_ALGORITHM)
        // 初始化公钥
        val x509KeySpec = X509EncodedKeySpec(publicKey)
        // 产生公钥
        val pubKey = keyFactory.generatePublic(x509KeySpec)
        // 初始化私钥
        val pkcs8KeySpec = PKCS8EncodedKeySpec(privateKey)
        // 产生私钥
        val priKey = keyFactory.generatePrivate(pkcs8KeySpec)
        // 实例化
        val keyAgree = KeyAgreement.getInstance(KEY_ALGORITHM, KEY_PROVIDER)
        // 初始化
        keyAgree.init(priKey)
        keyAgree.doPhase(pubKey, true)
        // 生成本地密钥
        val secretKey = keyAgree.generateSecret(SECRECT_ALGORITHM)
        return secretKey.encoded
    }
}