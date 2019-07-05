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

package com.tencent.devops.common.web.jasypt

import com.tencent.devops.common.api.util.AESUtil
import com.tencent.devops.common.api.util.SecurityUtil
import org.jasypt.encryption.StringEncryptor

class DefaultEncryptor : StringEncryptor {
    private val KEY = "rAFOey00bcuMNMrt"

    override fun decrypt(message: String): String {
        return AESUtil.decrypt(KEY, message)
    }

    override fun encrypt(message: String): String {
        return AESUtil.encrypt(KEY, message)
    }
}

fun main(args: Array<String>) {
    val encryptor = DefaultEncryptor()
    // dev
//    println("EFIfVh6Qh7ytySR1/gNKxQ== => ${encryptor.decrypt("EFIfVh6Qh7ytySR1/gNKxQ==")}")

    println("EFIfVh6Qh7ytySR1/gNKxQ== => ${SecurityUtil.decrypt("EFIfVh6Qh7ytySR1/gNKxQ==")}")
    println("JENKINS2014++ => ${SecurityUtil.encrypt("JENKINS2014++")}")
    println("devops => ${encryptor.encrypt("devops")}")
    println("JENKINS2014++ => ${encryptor.encrypt("JENKINS2014++")}")
    println("ITdev@server2 => ${encryptor.encrypt("ITdev@server2")}")
    println("iF26JkSsCVs52gZD => ${encryptor.encrypt("iF26JkSsCVs52gZD")}")
    println("N91Z8Xji1nxrg7h8 => ${encryptor.encrypt("N91Z8Xji1nxrg7h8")}")
    println()

    // test
    println("landun_test => ${encryptor.encrypt("landun_test")}")
    println("ITDev@db2 => ${encryptor.encrypt("ITDev@db2")}")
    println("redis@dev2018== => ${encryptor.encrypt("redis@dev2018==")}")
    println("im33XA59uBK0SSTV => ${encryptor.encrypt("im33XA59uBK0SSTV")}")
    println()
    // exp
    println("itdev@db => ${encryptor.encrypt("itdev@db")}")

    // prod
    println("bkdevops => ${encryptor.encrypt("bkdevops")}")
    println("ITDev@db2018 => ${encryptor.encrypt("ITDev@db2018")}")
    println("redis@dev2018== => ${encryptor.encrypt("redis@dev2018==")}")
    println("rnRghZgO3wM8RRAR => ${encryptor.encrypt("rnRghZgO3wM8RRAR")}")
    println()
}
