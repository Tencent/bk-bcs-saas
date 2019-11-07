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

package bcs

import (
	"encoding/json"
	"fmt"
	"time"

	"bcs_cc/config"
	"bcs_cc/logging"
	"bcs_cc/utils"
)

// agent info, include ip, etc,
type agentInfo struct {
	IP       string `json:"ip"`
	Disabled bool   `json:"disabled"`
}

// reserve metric info for mesos
type bcsReponseData struct {
	TotalDisk float64     `json:"disktotal"`
	UsedDisk  float64     `json:"diskused"`
	TotalMem  float64     `json:"memtotal"`
	UsedMem   float64     `json:"memused"`
	TotalCPU  float64     `json:"cputotal"`
	UsedCPU   float64     `json:"cpuused"`
	Agents    []agentInfo `json:"agents"`
}

type bcsResponse struct {
	Code    int            `json:"code"`
	Message string         `json:"message"`
	Data    bcsReponseData `json:"data"`
}

// MesosIPResource : get mesos resource info, in order to add or update node record
func MesosIPResource(clusterID string, env string, accessToken string) ([]map[string]string, error) {
	confBase := config.GlobalConfigurations
	reqURL := fmt.Sprintf("%s/%s%s", confBase.APIGWConf.Host, env, confBase.BCSConf.MesosResourcePath)
	params := fmt.Sprintf("access_token=%s", accessToken)
	// compose the request
	req := utils.GoReq{
		Method:  "GET",
		URL:     reqURL,
		Params:  params,
		Data:    make(map[string]interface{}),
		Header:  map[string]string{"Content-Type": "application/json", "BCS-ClusterID": clusterID},
		Timeout: time.Duration(10),
	}
	body, err := utils.RequestClient(req, confBase.APIGWConf.Proxy)
	if err != nil {
		logging.Error("request bcs api error，url: %v, detail: %v", reqURL, err)
		return nil, err
	}
	var bcsResp bcsResponse
	if err := json.Unmarshal([]byte(body), &bcsResp); err != nil {
		logging.Error("parse bcs response error, cluster_id: %s, detial: %v", clusterID, err)
		return nil, err
	}
	if bcsResp.Code != 0 {
		logging.Error("bcs api response error，cluster_id: %s, url: %v, detail: %v", clusterID, reqURL, bcsResp.Message)
		return nil, fmt.Errorf("request bcs error")
	}
	var nodeList []map[string]string
	// mesos status is normal if ip in agent
	for _, agent := range bcsResp.Data.Agents {
		status := utils.Normal
		if agent.Disabled {
			status = utils.ToRemoved
		}
		nodeList = append(nodeList, map[string]string{"ip": agent.IP, "status": status})
	}

	return nodeList, nil
}
