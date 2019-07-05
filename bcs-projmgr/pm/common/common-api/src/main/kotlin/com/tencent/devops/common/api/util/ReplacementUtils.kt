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

object ReplacementUtils {

    fun replace(command: String, replacement: KeyReplacement): String {
        if (command.isBlank()) {
            return command
        }
        val sb = StringBuilder()

        val lines = command.lines()
        lines.forEachIndexed { index, line ->
            // 忽略注释
            val template = if (line.trim().startsWith("#")) {
                line
            } else {
                parseTemplate(line, replacement)
            }
            sb.append(template)
            if (index != lines.size - 1) {
                sb.append("\n")
            }
        }
        return sb.toString()
    }
    private fun parseTemplate(command: String, replacement: KeyReplacement): String {
        if (command.isBlank()) {
            return command
        }
        val newValue = StringBuilder()
        var index = 0
        while (index < command.length) {
            val c = command[index]
            if (c == '$' && (index + 1) < command.length && command[index + 1] == '{') {
                val inside = StringBuilder()
                index = parseVariable(command, index + 2, inside, replacement)
                newValue.append(inside)
            } else {
                newValue.append(c)
                index++
            }
        }
        return newValue.toString()
    }

    private fun parseVariable(command: String, start: Int, newValue: StringBuilder, replacement: KeyReplacement): Int {
        val token = StringBuilder()
        var index = start
        while (index < command.length) {
            val c = command[index]
            if (c == '$' && (index + 1) < command.length && command[index + 1] == '{') {
                val inside = StringBuilder()
                index = parseVariable(command, index + 2, inside, replacement)
                token.append(inside)
            } else if (c == '}') {
                val tokenValue = getVariable(token.toString(), replacement) ?: "\${$token}"
                newValue.append(tokenValue)
                return index + 1
            } else {
                token.append(c)
                index++
            }
        }
        newValue.append("\${").append(token)
        return index
    }

    private fun getVariable(key: String, replacement: KeyReplacement) = replacement.getReplacement(key)

    interface KeyReplacement {
        fun getReplacement(key: String): String?
    }
}