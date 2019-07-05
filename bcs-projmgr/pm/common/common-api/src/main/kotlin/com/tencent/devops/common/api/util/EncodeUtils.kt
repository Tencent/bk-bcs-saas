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

import java.io.BufferedReader
import java.io.IOException
import java.io.StringReader
import java.net.URLEncoder
import java.util.logging.Level
import java.util.logging.Logger

object EncodeUtils {

    private val logger = Logger.getLogger(EncodeUtils::class.java.name)

    fun encodeYml(yml: String): String {
        val sb = StringBuilder()

        val br = BufferedReader(StringReader(yml))

        try {
            var line: String? = br.readLine()
            while (line != null) {
                if (line.trim { it <= ' ' }.startsWith("-")) {
                    line = encodeLine(line)
                }
                sb.append(line).append("\n")
                line = br.readLine()
            }

            return sb.toString()
        } catch (e: IOException) {
            logger.log(Level.WARNING, "Fail to encode the yml - " + yml, e)
            throw e
        }
    }

    fun decodeYml(yml: String): String {
        val sb = StringBuilder()

        val br = BufferedReader(StringReader(yml))

        try {
            var line: String? = br.readLine()
            while (line != null) {
                if (line.trim { it <= ' ' }.startsWith("-")) {
                    line = decodeLine(line)
                }
                sb.append(line).append("\n")
                line = br.readLine()
            }

            return sb.toString()
        } catch (e: IOException) {
            logger.log(Level.WARNING, "Fail to decode the yml - " + yml, e)
            throw e
        }
    }

    fun encodeLine(line: String): String {
        return line.replace(": ", URLEncoder.encode(": ", "utf-8"))
    }

    fun decodeLine(line: String): String {
        return line.replace(URLEncoder.encode(": ", "utf-8"), ": ")
    }
}