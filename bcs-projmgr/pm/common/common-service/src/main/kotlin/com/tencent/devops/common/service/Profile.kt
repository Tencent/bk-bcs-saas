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

package com.tencent.devops.common.service

import com.tencent.devops.common.service.env.Env
import org.springframework.core.env.Environment
import org.springframework.stereotype.Component

const val PROFILE_DEFAULT = "default"
const val PROFILE_INNER = "inner"

const val PROFILE_DEVELOPMENT = "dev"
const val PROFILE_PRODUCTION = "prod"
const val PROFILE_TEST = "test"
const val PROFILE_EXP = "exp"

@Component
class Profile(private val environment: Environment) {

    private val activeProfiles = environment.activeProfiles

    fun isDebug(): Boolean {
        return activeProfiles.isEmpty() || activeProfiles.contains(PROFILE_DEFAULT) || activeProfiles.contains(PROFILE_DEVELOPMENT) || activeProfiles.contains(PROFILE_TEST)
    }

    fun isDev(): Boolean {
        return activeProfiles.contains(PROFILE_DEVELOPMENT)
    }

    fun isExp(): Boolean {
        return activeProfiles.contains(PROFILE_EXP)
    }

    fun isTest(): Boolean {
        return activeProfiles.contains(PROFILE_TEST)
    }

    fun isProd(): Boolean {
        return activeProfiles.contains(PROFILE_PRODUCTION)
    }

    fun isLocal() =
            activeProfiles.contains(PROFILE_DEFAULT)

    fun getEnv(): Env {
        return when {
            isProd() -> Env.PROD
            isTest() -> Env.TEST
            isDev() -> Env.DEV
            isLocal() -> Env.DEFAULT
            else -> Env.PROD
        }
    }

    fun isInEnv(profileNames: Set<String>): Boolean {
        if (activeProfiles.isEmpty() && profileNames.contains(PROFILE_DEFAULT)) {
            return true
        }
        return profileNames.any { activeProfiles.contains(it) }
    }

    fun getActiveProfiles() = activeProfiles

    fun getApplicationName() = environment.getProperty("spring.application.name")
}