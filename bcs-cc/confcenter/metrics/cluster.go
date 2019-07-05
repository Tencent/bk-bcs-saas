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

package metrics

import (
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"bcs_cc/config"
	"bcs_cc/logging"
	"bcs_cc/storage/models"
	"bcs_cc/utils"

	"github.com/mitchellh/mapstructure"
)

var (
	bcsError = errors.New("request bcs error")

	bcsAPIEnv = map[string]string{
		"stag":  "uat",
		"debug": "debug",
		"prod":  "prod",
	}
)

type accessTokenData struct {
	AccessToken string `json:"access_token"`
}

type accessTokenResponse struct {
	Code    int             `json:"code"`
	Data    accessTokenData `json:"data"`
	Message string          `json:"message"`
}

type agentInfo struct {
	IP string `json:"ip"`
}

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

func requestBCSAPI(clusterID string, env string, clusterType string, confBase *config.Configurations, accessToken string) (bcsReponseData, error) {
	emptyInfo := bcsReponseData{}
	urlStr := "%v/api/apigw/bcs_api/%v/v4/scheduler/%v/cluster/resources"
	reqURL := fmt.Sprintf(urlStr, confBase.APIGWConf.Host, env, clusterType)
	params := fmt.Sprintf("access_token=%s", accessToken)
	headers := map[string]string{
		"Content-Type":  "application/json",
		"BCS-ClusterID": clusterID,
	}
	// compose the request
	req := utils.GoReq{
		Method:  "GET",
		URL:     reqURL,
		Params:  params,
		Data:    make(map[string]interface{}),
		Header:  headers,
		Timeout: time.Duration(10),
	}
	body, err := utils.RequestClient(req, confBase.APIGWConf.Proxy)
	if err != nil {
		logging.Error("request bcs api error，url: %v, detail: %v", reqURL, err)
		return emptyInfo, err
	}
	var bcsResponseInst bcsResponse
	if err := json.Unmarshal([]byte(body), &bcsResponseInst); err != nil {
		logging.Error("parse bcs response error, detial: %v", err)
		return emptyInfo, err
	}
	if bcsResponseInst.Code != 0 {
		logging.Error("bcs api response error， url: %v, detail: %v", reqURL, bcsResponseInst.Message)
		return emptyInfo, bcsError
	}
	return bcsResponseInst.Data, nil
}

func updateClusterMetric(info models.Cluster, env string, confBase *config.Configurations, accessToken string) error {
	bcsReponseDataInst, err := requestBCSAPI(info.ClusterID, env, info.Type, confBase, accessToken)
	if err != nil {
		return err
	}
	metricInfo := map[string]float64{
		"TotalMem":   bcsReponseDataInst.TotalMem,
		"RemainMem":  bcsReponseDataInst.TotalMem - bcsReponseDataInst.UsedMem,
		"TotalCPU":   bcsReponseDataInst.TotalCPU,
		"RemainCPU":  bcsReponseDataInst.TotalCPU - bcsReponseDataInst.UsedCPU,
		"TotalDisk":  bcsReponseDataInst.TotalDisk,
		"RemainDisk": bcsReponseDataInst.TotalDisk - bcsReponseDataInst.UsedDisk,
	}
	updater := models.UpdateClusterDataJSON{ProjectID: info.ProjectID, ClusterID: info.ClusterID}
	if err := mapstructure.Decode(metricInfo, &updater); err != nil {
		return err
	}
	if err := updater.UpdateRecord(); err != nil {
		logging.Error("update cluster error, cluster_id: %s, detail: %v", info.ClusterID, err)
		return err
	}
	currTimeStr := time.Now().Format("2006-01-02 15:04:05")
	tm, _ := time.ParseInLocation("2006-01-02 15:04:05", currTimeStr, time.Local)
	historyData := models.ClusterHistoryData{
		ProjectID:         info.ProjectID,
		ClusterID:         info.ClusterID,
		CapacityUpdatedAt: tm,
		Environment:       info.Environment,
	}
	if err := mapstructure.Decode(metricInfo, &historyData); err != nil {
		return err
	}
	if err := historyData.CreateRecord(); err != nil {
		return err
	}
	// update node status
	var normalNodeList []string
	for _, val := range bcsReponseDataInst.Agents {
		normalNodeList = append(normalNodeList, val.IP)
	}
	if err := models.UpdateNodeNormalNotReady(info.ClusterID, normalNodeList); err != nil {
		logging.Error("update node status error, detail: %v", err)
	}
	logging.Info("update cluster %s metric success", info.ClusterID)
	return nil
}

// ClusterMetric : the metric for cluster
func ClusterMetric() {
	logging.Info("Update cluster metric info ...")
	confBase := config.GlobalConfigurations
	clusterData, err := models.ClusterWithoutRemoved([]string{"removed"})
	// cluster is null, flow stop
	if err != nil || len(clusterData) == 0 {
		return
	}

	accessToken, err := getAccessToken(confBase)
	if err != nil {
		return
	}
	for _, cluster := range clusterData {
		currENV := bcsAPIEnv[cluster.Environment]
		go updateClusterMetric(cluster, currENV, confBase, accessToken)
	}

}
