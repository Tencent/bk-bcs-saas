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

package com.tencent.devops.common.api.enum

enum class AgentStatus(val status: Int) {
    UN_IMPORT(0), // 未导入，用户刚刚在界面上面生成链接
    UN_IMPORT_OK(1), // 未导入但是agent状态正常（这个时候还是不能用来当构建机）
    IMPORT_OK(2), // 用户已经在界面导入并且agent工作正常（构建机只有在这个状态才能正常工作）
    IMPORT_EXCEPTION(3), // agent异常
    DELETE(4);

    override fun toString() = status.toString()

    companion object {
        fun fromStatus(status: Int): AgentStatus {
            AgentStatus.values().forEach {
                if (status == it.status) {
                    return it
                }
            }
            throw RuntimeException("Unknown agent status($status)")
        }

        fun isDelete(status: AgentStatus) =
                status == DELETE

        fun isUnImport(status: AgentStatus) = status == UN_IMPORT

        fun isImportException(status: AgentStatus) = status == IMPORT_EXCEPTION
    }
}