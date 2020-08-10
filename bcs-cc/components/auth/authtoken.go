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
	"fmt"
	"time"

	"bcs_cc/config"
	"bcs_cc/logging"
	"bcs_cc/utils"
)

type accessTokenData struct {
	AccessToken string `json:"access_token"`
}

type accessTokenResponse struct {
	Code    int             `json:"code"`
	Data    accessTokenData `json:"data"`
	Message string          `json:"message"`
}

// GetAccessToken : get access token by auth
func GetAccessToken() (string, error) {
	// get request url
	confBase := config.GlobalConfigurations
	authConf := confBase.AuthConf
	reqURL := fmt.Sprintf("%s%s", authConf.Host, authConf.AuthTokenPath)
	reqData := map[string]interface{}{
		"id_provider": "client",
		"grant_type":  "client_credentials",
		"env_name":    "prod",
	}
	headers := map[string]string{
		"Content-Type":    "application/json",
		"X-BK-APP-CODE":   confBase.CCAppCode,
		"X-BK-APP-SECRET": confBase.CCAppSecret,
	}
	// compose the request
	req := utils.GoReq{
		Method:  "POST",
		URL:     reqURL,
		Params:  "",
		Data:    reqData,
		Header:  headers,
		Timeout: time.Duration(10),
	}
	body, err := utils.RequestClient(req, authConf.Proxy)
	if err != nil {
		return "", err
	}
	var accessTokenResp accessTokenResponse
	if err := json.Unmarshal([]byte(body), &accessTokenResp); err != nil {
		logging.Error("parse the access token data error，url: %v, body: %v, detail: %v", reqURL, body, err)
		return "", err
	}
	return accessTokenResp.Data.AccessToken, nil
}
