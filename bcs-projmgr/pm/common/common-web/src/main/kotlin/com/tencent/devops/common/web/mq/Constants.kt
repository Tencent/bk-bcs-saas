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

package com.tencent.devops.common.web.mq

const val QUEUE_PIPELINE_BUILD = "queue_pipeline_build"
const val QUEUE_PIPELINE_BUILD_NEED_END = "queue_pipeline_build_need_end"
const val EXCHANGE_PIPELINE_BUILD = "exchange_pipeline_build"
const val ROUTE_PIPELINE_BUILD = "route_pipeline_build"
const val ROUTE_PIPELINE_BUILD_NEED_END = "route_pipeline_build_need_end"

const val ROUTE_PIPELINE_FINISH = "route_pipeline_finish"
const val QUEUE_PIPELINE_FINISH = "queue_pipeline_finish"
const val EXCHANGE_PIPELINE_FINISH = "exchange_pipeline_finish"

const val ROUTE_NOTIFY_MESSAGE = "route_notify_message"
const val QUEUE_NOTIFY_MESSAGE = "queue_notify_message"
const val EXCHANGE_NOTIFY_MESSAGE = "exchange_notify_message"

const val ROUTE_PAASCC_PROJECT_CREATE = "route_paascc_project_create"
const val QUEUE_PAASCC_PROJECT_CREATE = "queue_paascc_project_create"
const val EXCHANGE_PAASCC_PROJECT_CREATE = "exchange_paascc_project_create"

const val ROUTE_PAASCC_PROJECT_UPDATE = "route_paascc_project_update"
const val QUEUE_PAASCC_PROJECT_UPDATE = "queue_paascc_project_update"
const val EXCHANGE_PAASCC_PROJECT_UPDATE = "exchange_paascc_project_update"

const val EXCHANGE_PAASCC_PROJECT_UPDATE_LOGO = "exchange_paascc_project_update_logo"
const val ROUTE_PAASCC_PROJECT_UPDATE_LOGO = "route_paascc_project_update_logo"
const val QUEUE_PAASCC_PROJECT_UPDATE_LOGO = "queue_paascc_project_update_logo"