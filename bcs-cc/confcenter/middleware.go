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

package confcenter

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"time"

	"bcs-cc/components/auth"
	"bcs-cc/config"
	"bcs-cc/logging"
	"bcs-cc/utils"

	jwt "github.com/dgrijalva/jwt-go"
	"github.com/gin-gonic/gin"
)

type accessTokenInfo struct {
	AccessToken string `json:"access_token"`
}

func parseJwt(c *gin.Context) error {
	// get jwt info from headers
	JWTInfo := c.GetHeader("X-Bkapi-Jwt")
	if JWTInfo == "" {
		return errors.New("header[X-Bkapi-Jwt] is null")
	}
	// parse the token
	token, err := utils.DecodeJwtToken(JWTInfo)
	if err != nil {
		return err
	}
	// set handle claims
	JWTToken := token.(jwt.MapClaims)
	// Assert with map for specific field value， include user, app
	userInfoMap, ok := JWTToken["user"].(map[string]interface{})
	if ok && userInfoMap["username"] != nil {
		c.Set("Username", userInfoMap["username"])
	}
	appInfoMap, ok := JWTToken["app"].(map[string]interface{})
	if ok && appInfoMap["app_code"] != nil {
		c.Set("AppCode", appInfoMap["app_code"])
	}
	return nil
}

func parseAccessToken(c *gin.Context) error {
	// get auth token
	// 1. get token from params
	accessToken := c.Query("access_token")
	if accessToken == "" {
		// 2. get token from header
		tokenInfo := c.GetHeader("X-Bkapi-Authorization")
		if tokenInfo == "" {
			return errors.New("access token is null")
		}
		accessTokenData := &accessTokenInfo{}
		if err := json.Unmarshal([]byte(tokenInfo), accessTokenData); err != nil {
			logging.Error("header[X-BKAPI-AUTHORIZATION] parse error, detail %v", err)
			return errors.New("header[X-BKAPI-AUTHORIZATION] parse error")
		}
		accessToken = accessTokenData.AccessToken
	}
	tokenData, err := auth.VerifyAuthToken(accessToken)
	if err != nil {
		return err
	}
	// set the usename and app_code
	c.Set("Username", tokenData["username"])
	c.Set("AppCode", tokenData["app_code"])
	return nil
}

// JWTTokenMiddleware : jwt middleware handler
func JWTTokenMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		if config.GlobalConfigurations.APIGWConf.IdentityFromJWT {
			if err := parseJwt(c); err != nil {
				utils.BadReqJSONResponse(c, err)
				c.Abort()
				return
			}
		} else {
			if err := parseAccessToken(c); err != nil {
				utils.BadReqJSONResponse(c, err)
				c.Abort()
				return
			}
		}
		c.Next()
	}
}

// https://stackoverflow.com/questions/38501325/how-to-log-response-body-in-gin
// respWriter : resp writer
type respWriter struct {
	gin.ResponseWriter
	body *bytes.Buffer
}

// Write : write info
func (w respWriter) Write(b []byte) (int, error) {
	w.body.Write(b)
	return w.ResponseWriter.Write(b)
}

// get request id
func getRequestID(c *gin.Context) string {
	requestID := c.GetHeader("X-Bkapi-Request-Id")
	if requestID == "" {
		requestID = utils.NewUUID()
	}
	return requestID
}

func readData(c *gin.Context) []byte {
	buf, _ := ioutil.ReadAll(c.Request.Body)
	bufOne := ioutil.NopCloser(bytes.NewBuffer(buf))
	bufTwo := ioutil.NopCloser(bytes.NewBuffer(buf))
	c.Request.Body = bufTwo
	// read the data
	data, _ := ioutil.ReadAll(bufOne)
	switch dataLen := len(data); {
	case dataLen > 1000:
		data = data[:1000]
	case dataLen == 0: // define a common message
		data = []byte("BCS configure center")
	default:
		data = data[0:dataLen]
	}
	return data
}

// RequestLogMiddleware : record the request log
func RequestLogMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		data := readData(c)
		startTime := time.Now()
		// request_id maybe from api gateway
		requestID := getRequestID(c)
		// transfer the request_id
		c.Set("request_id", requestID)
		blw := &respWriter{body: bytes.NewBufferString(""), ResponseWriter: c.Writer}
		c.Writer = blw
		// response for user request
		c.Next()
		costTime := time.Since(startTime)
		// compose the detail
		reqParams := c.Request.URL.Query()
		// handle the error
		reqParamsStr, err := json.Marshal(reqParams)
		if err != nil {
			reqParamsStr = []byte(fmt.Sprintf("%v", reqParams))
		}
		// detail info
		logInfoDetail := map[string]interface{}{
			"request_id": requestID,
			"req_path":   c.Request.URL.Path,
			"req_method": c.Request.Method,
			"req_params": string(reqParamsStr),
			"req_data":   string(data),
			"cost_msecs": fmt.Sprintf("%.3f ms", costTime.Seconds()*1000),
			"client_ip":  c.ClientIP(),
			"tags":       [3]string{"env::sz.prod", "paas", "bcs_cc"},
			"level":      "info",
			"type":       "",
			"resp_data":  blw.body.String(),
		}
		jsonStr, err := json.Marshal(logInfoDetail)
		if err != nil {
			jsonStr = []byte(fmt.Sprintf("%v", logInfoDetail))
		}
		logging.Info(string(jsonStr))
	}
}
