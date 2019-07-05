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

package models

import (
	"reflect"
)

// DataInterface :
type DataInterface interface {
	CreateOrUpdateRecord() error
	UpdateRecord() error
	CreateRecord() error
	RetriveRecord() error
}

// Serializer : 序列化
func Serializer(src reflect.Type, val reflect.Value) map[string]interface{} {
	dataSLZ := make(map[string]interface{})
	for i := 0; i < val.NumField(); i++ {
		// 判断字段可以导出, 防止出现异常
		if val.Field(i).CanInterface() {
			name := src.Field(i).Tag.Get("json")
			dataSLZ[name] = val.Field(i).Interface()
		}
	}
	return dataSLZ
}
