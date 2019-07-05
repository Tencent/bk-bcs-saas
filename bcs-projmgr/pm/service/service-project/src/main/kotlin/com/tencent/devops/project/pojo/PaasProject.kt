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

package com.tencent.devops.project.pojo

import java.util.Date

data class PaasProject(
    val approval_status: Int,
    val approval_time: String,
    val approver: String,
    val bg_id: Int,
    val bg_name: String,
    val cc_app_id: Int,
    val center_id: Int,
    val center_name: String,
    val created_at: Date,
    val creator: String,
    val data_id: Int,
    val deploy_type: String,
    val dept_id: Int,
    val dept_name: String,
    val description: String,
    val english_name: String,
    val extra: Any,
    val is_offlined: Boolean,
    val is_secrecy: Boolean,
    val kind: Int,
    val logo_addr: String,
    val project_id: String,
    val project_name: String,
    val project_type: Int,
    val remark: String,
    val updated_at: Date?,
    val use_bk: Boolean
)