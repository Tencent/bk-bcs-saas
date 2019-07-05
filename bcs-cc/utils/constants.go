/*
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

package utils

// Error Codes
const (
	NoError                = 0
	RejectErr              = 2001200
	UnknownError           = 2001300
	UserError              = 2001400
	SystemError            = 2001500
	DBError                = 2001600
	IPAreadyExsit          = 1001
	ClusterNameDuplicate   = 1002
	NamespaceNameDuplicate = 1003
	NotPermission          = 4003
)

// db error
const (
	ERDUPENTRY = 1062 // Duplicate entry
)
