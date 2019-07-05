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

package com.tencent.devops.common.web.utils

import javax.servlet.http.HttpServletRequest

object CookieUtil {
    fun getCookieValue(request: HttpServletRequest, name: String): String? {
        var value: String? = null

        // cookie数组
        val cookies = request.cookies
        if (null != cookies) {
            for (cookie in cookies) {
                if (cookie.name == name) {
                    value = cookie.value
                    break
                }
            }
        }

        if (null == value) {
            // Cookie属性中没有获取到，那么从Headers里面获取
            var cookieStr: String? = request.getHeader("Cookie")
            if (cookieStr != null) {
                // 去掉所有空白字符，不限于空格
                cookieStr = cookieStr.replace("\\s*".toRegex(), "")
                val cookieArr = cookieStr.split(";".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()

                for (cookieItem in cookieArr) {
                    val cookieItemArr = cookieItem.split("=".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
                    if (cookieItemArr[0] == name) {
                        value = cookieItemArr[1]
                        break
                    }
                }
            }
        }
        return value
    }
}