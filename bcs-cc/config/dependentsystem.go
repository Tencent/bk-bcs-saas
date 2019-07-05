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

package config

// AuthConfInfo : auth config Info
type AuthConfInfo struct {
	Host            string `yaml:"host"`
	Proxy           string `yaml:"proxy"`
	AuthTokenPath   string `yaml:"auth_token_path"`
	AuthProjectPath string `yaml:"auth_project_path"`
	AuthVerifyPath  string `yaml:"auth_verify_path"`
}

// APIGWConfInfo : apigw config info
type APIGWConfInfo struct {
	IdentityFromJWT bool   `yaml:"identity_from_jwt"`
	Host            string `yaml:"host"`
	Proxy           string `yaml:"proxy"`
}

// Init : init default conf
func (auth *AuthConfInfo) Init() error {
	auth.Host = "http://iam.service.consul"
	auth.Proxy = ""
	auth.AuthTokenPath = "/bkiam/api/v1/auth/access-tokens"
	auth.AuthProjectPath = "/bkiam/api/v1/perm/scope_type/project/authorized-scopes/"
	auth.AuthVerifyPath = "/bkiam/api/v1/auth/access-tokens/verify"
	return nil
}

// Init : init default conf
func (apigw *APIGWConfInfo) Init() error {
	apigw.IdentityFromJWT = true
	apigw.Host = "http://paas.service.consul"
	apigw.Proxy = ""
	return nil
}
