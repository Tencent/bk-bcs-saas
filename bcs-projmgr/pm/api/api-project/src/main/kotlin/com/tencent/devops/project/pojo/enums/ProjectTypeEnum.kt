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

package com.tencent.devops.project.pojo.enums

enum class ProjectTypeEnum(val index: Int) {
    MOBILE_GAME(1) {
        override fun getPerson(ordinal: Int): String {
            return "手游"
        }
    },
    CLIENT_GAME(2) {
        override fun getPerson(ordinal: Int): String {
            return "端游"
        }
    },
    WEBPAGE_GAME(3) {
        override fun getPerson(ordinal: Int): String {
            return "页游"
        }
    },
    PLATFORM_PRODUCT(4) {
        override fun getPerson(ordinal: Int): String {
            return "平台产品"
        }
    },
    SUPPORT_PRODUCT(5) {
        override fun getPerson(ordinal: Int): String {
            return "支撑产品"
        }
    };

    abstract fun getPerson(ordinal: Int): String
}