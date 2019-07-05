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

package auth

import (
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"bcs_cc/config"
	"bcs_cc/logging"
	"bcs_cc/utils"
)

type verifyData struct {
	BkAppCode string            `json:"bk_app_code"`
	Identity  map[string]string `json:"identity"`
}

type verifyRespBody struct {
	Code    uint       `json:"code"`
	Data    verifyData `json:"data"`
	Message string     `json:"message"`
}

// VerifyAuthToken : verify auth token
func VerifyAuthToken(token string) (map[string]string, error) {
	// get request url
	authConf := config.GlobalConfigurations.AuthConf
	reqURL := fmt.Sprintf("%s%s", authConf.Host, authConf.AuthVerifyPath)
	headers := map[string]string{
		"Content-Type":    "application/json",
		"X-BK-APP-CODE":   config.GlobalConfigurations.CCAppCode,
		"X-BK-APP-SECRET": config.GlobalConfigurations.CCAppSecret,
	}
	req := utils.GoReq{
		Method:  "POST",
		URL:     reqURL,
		Params:  "",
		Data:    map[string]interface{}{"access_token": token},
		Timeout: time.Duration(10),
		Header:  headers,
	}
	body, err := utils.RequestClient(req, authConf.Proxy)
	if err != nil {
		return nil, err
	}
	respContent := verifyRespBody{}
	if err := json.Unmarshal([]byte(body), &respContent); err != nil {
		logging.Error("verify token response parse failed，detail: %v", err)
		return nil, err
	}
	if respContent.Code != 0 {
		logging.Error("verify token request error， response message: %v", respContent.Message)
		return nil, errors.New(respContent.Message)
	}
	respData := respContent.Data
	return map[string]string{
		"app_code": respData.BkAppCode,
		"username": respData.Identity["username"],
	}, nil
}
