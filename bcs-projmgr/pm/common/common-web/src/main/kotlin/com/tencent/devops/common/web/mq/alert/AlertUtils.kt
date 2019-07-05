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

package com.tencent.devops.common.web.mq.alert

import com.tencent.devops.common.service.Profile
import com.tencent.devops.common.web.mq.EXCHANGE_NOTIFY_MESSAGE
import com.tencent.devops.common.web.mq.ROUTE_NOTIFY_MESSAGE
import com.tencent.devops.common.service.utils.SpringContextUtil
import org.slf4j.LoggerFactory
import org.springframework.amqp.rabbit.core.RabbitTemplate

object AlertUtils {

    fun doAlert(level: AlertLevel, title: String, message: String) {
        val serviceName = SpringContextUtil.getBean(Profile::class.java).getApplicationName() ?: ""
        doAlert(serviceName, level, title, message)
    }

    fun doAlert(module: String, level: AlertLevel, title: String, message: String) {
        try {
            val alert = Alert(module, level, title, message)
            logger.info("Start to send the notify $alert")
            // 企业版不发布通知。
//            val rabbitTemplate = SpringContextUtil.getBean(RabbitTemplate::class.java)
//            rabbitTemplate.convertAndSend(EXCHANGE_NOTIFY_MESSAGE, ROUTE_NOTIFY_MESSAGE, alert)
        } catch (t: Throwable) {
            logger.warn("Fail to send the notify alert (level=$level, title=$title, message=$message)", t)
        }
    }

    private val logger = LoggerFactory.getLogger(AlertUtils::class.java)
}