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
	"strings"
	"time"

	"bcs-cc/config"
	"bcs-cc/logging"
	"bcs-cc/utils"
)

var defaultClusterState = "bcs_new"

type agentClusterIDResp struct {
	ID      string `json:"id"`
	Message string `json:"message"`
}

type credentialsResp struct {
	ServerAddressPath string `json:"server_address_path"`
	Message           string `json:"message"`
}

type nodeListStatus struct {
	Addresses  []map[string]string `json:"addresses"`
	Conditions []map[string]string `json:"conditions"`
}

type nodeListSpec struct {
	Unschedulable bool `json:"unschedulable"`
}

type nodeListMetadata struct {
	Labels map[string]string `json:"labels"`
}

type nodeListRecord struct {
	Metadata nodeListMetadata `json:"metadata"`
	Spec     nodeListSpec     `json:"spec"`
	Status   nodeListStatus   `json:"status"`
}

type nodeListResp struct {
	Items []nodeListRecord `json:"items"`
}

func queryK8sAgentClusterID(projectID string, clusterID string, env string, accessToken string) (string, error) {
	confBase := config.GlobalConfigurations
	// 直接连接bcs api
	host, _ := confBase.BCSConf.Hosts[env]
	reqURL := fmt.Sprintf("%s%s", host, confBase.BCSConf.K8sQueryClusterIDPath)
	params := fmt.Sprintf("access_token=%s&project_id=%s&cluster_id=%s", accessToken, projectID, clusterID)
	req := utils.GoReq{
		Method:  "GET",
		URL:     reqURL,
		Params:  params,
		Data:    make(map[string]interface{}),
		Header:  map[string]string{"Content-Type": "application/json", "Authorization": confBase.BCSConf.Authorization},
		Timeout: time.Duration(10),
	}
	body, err := utils.RequestClient(req, confBase.APIGWConf.Proxy)
	if err != nil {
		logging.Error("request bcs api error，url: %v, detail: %v", reqURL, err)
		return "", err
	}
	var resp agentClusterIDResp
	if err := json.Unmarshal([]byte(body), &resp); err != nil {
		logging.Error("parse bcs response error, cluster_id: %s, detial: %v", clusterID, err)
		return "", err
	}
	if resp.Message != "" {
		logging.Error("bcs api response error，cluster_id: %s, url: %v, detail: %v", clusterID, reqURL, resp.Message)
		return "", fmt.Errorf("request bcs error")
	}
	return resp.ID, nil
}

func queryCredentials(agentClusterID string, env string, accessToken string) (string, error) {
	confBase := config.GlobalConfigurations
	reqPath := fmt.Sprintf(confBase.BCSConf.K8sQueryCredentialsPath, agentClusterID)
	host, _ := confBase.BCSConf.Hosts[env]
	reqURL := fmt.Sprintf("%s%s", host, reqPath)
	params := fmt.Sprintf("access_token=%s", accessToken)
	req := utils.GoReq{
		Method:  "GET",
		URL:     reqURL,
		Params:  params,
		Data:    make(map[string]interface{}),
		Header:  map[string]string{"Content-Type": "application/json", "Authorization": confBase.BCSConf.Authorization},
		Timeout: time.Duration(10),
	}
	body, err := utils.RequestClient(req, confBase.APIGWConf.Proxy)
	if err != nil {
		logging.Error("request bcs api error，url: %v, detail: %v", reqURL, err)
		return "", err
	}
	var resp credentialsResp
	if err := json.Unmarshal([]byte(body), &resp); err != nil {
		logging.Error("parse bcs response error, cluster_id: %s, detial: %v", agentClusterID, err)
		return "", err
	}
	if resp.Message != "" {
		logging.Error("bcs api response error，cluster_id: %s, url: %v, detail: %v", agentClusterID, reqURL, resp.Message)
		return "", fmt.Errorf("request bcs error")
	}

	return resp.ServerAddressPath, nil
}

// compose the node list, include ip and status
func composeNodeList(resp nodeListResp, clusterState string) (nodeList []map[string]string) {
	isBCSNEWCluster := true
	if clusterState != defaultClusterState {
		isBCSNEWCluster = false
	}
	for _, info := range resp.Items {
		// 针对平台创建集群，获取角色为node的节点，进行保存
		nodeRole := info.Metadata.Labels["node-role.kubernetes.io/node"]
		if nodeRole != "true" && isBCSNEWCluster {
			continue
		}
		innerIP := ""
		addresses := info.Status.Addresses
		for _, host := range addresses {
			if host["type"] == "InternalIP" {
				innerIP = host["address"]
				break
			}
		}
		conditions := info.Status.Conditions
		status := utils.Normal
		for _, cond := range conditions {
			if cond["type"] == "Ready" && cond["status"] == "True" {
				status = utils.Normal
				if info.Spec.Unschedulable {
					status = utils.ToRemoved
				}
				break
			} else {
				status = utils.NotReady
			}
		}
		nodeList = append(nodeList, map[string]string{"ip": innerIP, "status": status})
	}
	return nodeList
}

func queryNodes(agentClusterID string, serverPath string, env string, accessToken string, clusterState string) ([]map[string]string, error) {
	confBase := config.GlobalConfigurations
	host := confBase.BCSConf.Hosts[env]
	serverPathTrim := strings.Trim(serverPath, "/")
	reqURL := fmt.Sprintf("%s/%s%s", host, serverPathTrim, confBase.BCSConf.K8sQueryNodesPath)
	params := fmt.Sprintf("access_token=%s", accessToken)
	headers := map[string]string{
		"Authorization":         confBase.BCSConf.Authorization,
		"Connection":            "Upgrade",
		"Host":                  host,
		"Origin":                host,
		"Sec-WebSocket-Key":     "SGVsbG8sIHdvcmxkIQ==",
		"Sec-WebSocket-Version": "13",
		"Upgrade":               "websocket",
	}
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
		return nil, err
	}
	var resp nodeListResp
	if err := json.Unmarshal([]byte(body), &resp); err != nil {
		logging.Error("parse bcs response error, cluster_id: %s, detial: %v", agentClusterID, err)
		return nil, err
	}
	return composeNodeList(resp, clusterState), nil
}

// K8sIPResource :
func K8sIPResource(projectID string, clusterID string, env string, accessToken string, clusterState string) ([]map[string]string, error) {
	// query k8s agent registered cluster id
	agentClusterID, err := queryK8sAgentClusterID(projectID, clusterID, env, accessToken)
	if err != nil {
		return nil, err
	}
	// query server prefix path for raw api
	serverPath, err := queryCredentials(agentClusterID, env, accessToken)
	if err != nil {
		return nil, err
	}
	return queryNodes(agentClusterID, serverPath, env, accessToken, clusterState)
}
