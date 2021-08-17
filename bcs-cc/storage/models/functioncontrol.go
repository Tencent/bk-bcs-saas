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
	"encoding/json"
	"fmt"

	"bcs-cc/storage"
	"bcs-cc/utils"
)

// FunctionControl : function controller
//go:generate goqueryset -in ${GOFILE} -out qs_${GOFILE}
// gen:qs
type FunctionControl struct {
	Model
	FuncCode    string `json:"func_code" gorm:"size:64;unique"`
	Description string `json:"description" gorm:"size:100"`
	FuncStatus  bool   `json:"func_status" gorm:"default:false"`
	WhiteList   string `json:"white_list" sql:"type:text"`
	Creator     string `json:"creator" gorm:"size:32"`
	Updator     string `json:"updator" gorm:"size:32"`
}

// RetriveRecord : retrive one record by function code
func (fc *FunctionControl) RetriveRecord() error {
	qs := NewFunctionControlQuerySet(storage.GetDefaultSession().DB)
	return qs.FuncCodeEq(fc.FuncCode).One(fc)
}

// CheckUserInWhiteList :
// 判断用户在有查询权限的用户白名单中
// NOTE: 仅内部版用到
func CheckUserInWhiteList(username string) error {
	userFuncCtl := &FunctionControl{FuncCode: "user_auth_list"}
	if err := userFuncCtl.RetriveRecord(); err != nil {
		return err
	}
	if !userFuncCtl.FuncStatus {
		return nil
	}
	var userWhiteList []string
	err := json.Unmarshal([]byte(userFuncCtl.WhiteList), &userWhiteList)
	if err != nil {
		return fmt.Errorf("Parse json error，detail: %v", err)
	}
	if utils.StringInSlice(username, userWhiteList) {
		return nil
	}
	return fmt.Errorf("username[%s] has not auth", username)
}
