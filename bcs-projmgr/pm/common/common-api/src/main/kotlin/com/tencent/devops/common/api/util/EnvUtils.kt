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

object EnvUtils {
    fun parseEnv(command: String, data: Map<String, String>, replaceWithEmpty: Boolean = false): String {
        if (command.isBlank()) {
            return command
        }
        val newValue = StringBuilder()
        var index = 0
        while (index < command.length) {
            val c = command[index]
            if (c == '$' && (index + 1) < command.length && command[index + 1] == '{') {
                val inside = StringBuilder()
                index = parseVariable(command, index + 2, inside, data, replaceWithEmpty)
                newValue.append(inside)
            } else {
                newValue.append(c)
                index++
            }
        }
        return newValue.toString()
    }

    private fun parseVariable(command: String, start: Int, newValue: StringBuilder, data: Map<String, String>, replaceWithEmpty: Boolean = false): Int {
        val token = StringBuilder()
        var index = start
        while (index < command.length) {
            val c = command[index]
            if (c == '$' && (index + 1) < command.length && command[index + 1] == '{') {
                val inside = StringBuilder()
                index = parseVariable(command, index + 2, inside, data, replaceWithEmpty)
                token.append(inside)
            } else if (c == '}') {
                val value = getVariable(data, token.toString()) ?: if (replaceWithEmpty) {
                    ""
                } else {
                    "\${$token}"
                }

                newValue.append(value)
                return index + 1
            } else {
                token.append(c)
                index++
            }
        }
        newValue.append("\${").append(token)
        return index
    }

    private fun getVariable(data: Map<String, String>, key: String) = if (data[key] != null) {
        data[key]!!
    } else {
        null
    }
}