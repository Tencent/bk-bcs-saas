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

package com.tencent.devops.project.pojo.tof

/**
 * {
"TypeId": "6",
"LeaderId": "73",
"Name": "IEG互动娱乐事业群",
"Level": "1",
"Enabled": "true",
"SecretaryId": "5095",
"TypeName": "20 系统",
"VicePresidentId": "73",
"ParentId": "0",
"ExProperties": "",
"ExchangeGroupName": " ",
"ID": "956"
}
 */
data class DeptInfo(
    val TypeId: String,
    val LeaderId: String,
    val Name: String,
    val Level: String,
    val Enabled: String,
    val ParentId: String,
    val ID: String

)