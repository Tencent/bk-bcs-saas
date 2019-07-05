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

package tests

import (
	"bcs_cc/storage/models"
	"reflect"
	"testing"
)

type testData struct {
	Name string `json:"name"`
	Age  uint   `json:"age"`
	Addr string `json:"_"`
}

func TestSerializer(t *testing.T) {
	test := testData{
		Name: "test",
		Age:  11,
		Addr: "test",
	}
	src := reflect.TypeOf(test)
	val := reflect.ValueOf(test)
	data := models.Serializer(src, val)
	name := data["name"].(string)
	_, ok := data["addr"]
	if ok {
		t.Error("addr应该不存在")
	}
	if name != test.Name {
		t.Error("序列化不正确")
	}
}
