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

package tasks

import (
	"bcs_cc/config"
	"encoding/json"
	"fmt"
	"paas-configcenter/logging"
	"paas-configcenter/utils"
	"time"
)

// get access token by
func getAccessToken(confBase *config.Configurations) (string, error) {
	reqURL := fmt.Sprintf("%s%s", confBase.AuthConf.Host, confBase.AuthConf.AuthTokenPath)
	reqData := map[string]interface{}{"id_provider": "client", "grant_type": "authorization_code"}
	// reqDataJSON, _ := json.Marshal(reqData)
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
	body, err := utils.RequestClient(req, confBase.AuthConf.Proxy)
	if err != nil {
		return "", err
	}
	var accessTokenRespInst accessTokenResponse
	if err := json.Unmarshal([]byte(body), &accessTokenRespInst); err != nil {
		logging.Error("parse the access token data error，url: %v, body: %v, detail: %v", reqURL, body, err)
		return "", err
	}
	return accessTokenRespInst.Data.AccessToken, nil
}

// SyncNodes : sync node info, and add/update node db record
func SyncNodes(projectID string, clusterID string) {
	conf := config.GlobalConfigurations
	if !conf.EnableSyncNodes {
		return
	}

}
