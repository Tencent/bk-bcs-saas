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

package com.tencent.devops.project.jmx.api

import org.springframework.jmx.export.annotation.ManagedAttribute
import org.springframework.jmx.export.annotation.ManagedResource
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong

@ManagedResource
class APIPerformanceBean {
    private val executeCount = AtomicInteger(0)
    private val executeElapse = AtomicLong(0)
    private val calculateCount = AtomicInteger(0)
    private val failureCount = AtomicInteger(0)

    @Synchronized
    fun execute(elapse: Long, success: Boolean) {
        executeElapse.addAndGet(elapse)
        executeCount.incrementAndGet()
        calculateCount.incrementAndGet()
        if (!success) {
            failureCount.incrementAndGet()
        }
    }

    @Synchronized
    @ManagedAttribute
    fun getExecutePerformance(): Double {
        val elapse = executeElapse.getAndSet(0)
        val count = calculateCount.getAndSet(0)
        return if (count == 0) {
            0.0
        } else {
            elapse.toDouble() / count
        }
    }

    @ManagedAttribute
    fun getExecuteCount() = executeCount.get()

    @ManagedAttribute
    fun getFailureCount() = failureCount.get()
}