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
	"errors"
	"fmt"
	"time"

	"bcs-cc/logging"
	"encoding/json"

	"github.com/gin-gonic/gin"
)

// MergeGinH : merger h2 to h1
func MergeGinH(h1 *gin.H, h2 *gin.H) *gin.H {
	for key, value := range *h2 {
		(*h1)[key] = value
	}
	return h1
}

// SimpleJSONResponse : simplae http response with default scope
func SimpleJSONResponse(c *gin.Context, status int, h *gin.H) {
	status = 200 // 真实状态码要通过返回json中的code字段来判断
	response := MergeGinH(&gin.H{
		"result":  false,
		"message": "ok",
		"code":    UnknownError,
		"data":    nil,
	}, h)
	// if exist, return
	(*response)["request_id"] = c.GetString("request_id")
	c.JSON(status, response)
}

// GetMessage : return candidate if format is empty
func GetMessage(candidate string, format string, v []interface{}) string {
	if format == "" {
		return candidate
	}
	if len(v) > 0 {
		return fmt.Sprintf(format, v...)
	}
	return format
}

// OKJSONResponse : return response with 400 status
func OKJSONResponse(c *gin.Context, h interface{}) {
	response := &gin.H{
		"result":  true,
		"code":    NoError,
		"message": "ok",
		"data":    h,
	}
	SimpleJSONResponse(c, 200, response)
}

// OKJSONResponseWithMessage : return response with 400 status
func OKJSONResponseWithMessage(c *gin.Context, h interface{}, message string, v ...interface{}) {
	response := &gin.H{
		"result":  true,
		"code":    NoError,
		"message": GetMessage("ok", message, v),
		"data":    h,
	}
	SimpleJSONResponse(c, 200, response)
}

// BadReqJSONResponse : return response with 400 status
func BadReqJSONResponse(c *gin.Context, err error, v ...interface{}) {
	response := &gin.H{
		"code":    UserError,
		"message": GetMessage("bad request", err.Error(), v),
	}
	SimpleJSONResponse(c, 400, response)
}

// DBErrorResponse : return DBError response with 2001600 status
func DBErrorResponse(c *gin.Context, err error, v ...interface{}) {
	response := &gin.H{
		"code":    DBError,
		"message": GetMessage("bad request", err.Error(), v),
	}
	SimpleJSONResponse(c, 500, response)
}

// NotFoundJSONResponse : return response with 404 status
func NotFoundJSONResponse(c *gin.Context, err error, v ...interface{}) {
	response := &gin.H{
		"code":    UserError,
		"message": GetMessage("not found", err.Error(), v),
	}
	SimpleJSONResponse(c, 404, response)
}

// SysErrorJSONResponse : return response with 500 status
func SysErrorJSONResponse(c *gin.Context, err error, v ...interface{}) {
	response := &gin.H{
		"code":    SystemError,
		"message": GetMessage("system error", err.Error(), v),
	}
	SimpleJSONResponse(c, 500, response)
}

// RequestClient : http request client for apis layer
func RequestClient(req GoReq, proxy string) (string, error) {
	client := NewRequest().SetTimeout(req.Timeout * time.Second)
	if proxy != "" {
		client = client.Proxy(proxy)
	}
	reqDataByte, err := json.Marshal(req.Data)
	if err != nil {
		return "", err
	}
	client = client.SendMapString(string(reqDataByte)).CustomMethod(req.Method, req.URL+"?"+req.Params)
	if len(req.Header) > 0 {
		for key, val := range req.Header {
			client = client.SetHeader(key, val)
		}
	}
	_, body, errs := client.End()
	var errStr string
	if len(errs) > 0 {
		errStr = ErrorList2String(errs)
		logging.Error("Request api exception，url: %v, detail: %v", req.URL, errStr)
		return "", errors.New(errStr)
	}
	return body, nil
}
