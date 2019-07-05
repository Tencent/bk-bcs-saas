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

package utils

import (
	"bcs_cc/config"
	"errors"
	"fmt"
	"io/ioutil"

	"github.com/dgrijalva/jwt-go"
)

// DecodeJwtToken : jwt decode
func DecodeJwtToken(jwtToken string) (claim jwt.Claims, customerr error) {
	// ras512 alg
	var parser = &jwt.Parser{ValidMethods: []string{"RS512"}}
	if parser == nil {
		parser = new(jwt.Parser)
	}
	// declair jwtotoken
	var token *jwt.Token
	var err error

	// parse the jwt token
	token, err = jwt.Parse(jwtToken, func(token *jwt.Token) (interface{}, error) {
		currPath := config.GlobalConfigurations.JWTPath
		if currPath == "" {
			currPath = "./config/cert/rsa512.pub"
		}
		publicKey, err := ioutil.ReadFile(currPath)
		if err != nil {
			return nil, fmt.Errorf("read the public key error, %v", err)
		}
		pubKey, err := jwt.ParseRSAPublicKeyFromPEM(publicKey)
		if err != nil {
			return nil, fmt.Errorf("parse the jwt token error, %v", err)
		}

		return pubKey, nil
	})

	// 处理异常
	if err != nil {
		return nil, err
	}
	if token.Valid {
		return token.Claims, nil
	}
	return nil, errors.New("verify jwt token failed")
}
