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
	"bcs-cc/logging"
	"encoding/hex"
	"fmt"
	"math/rand"
	"regexp"
	"strconv"
	"strings"
	"time"

	uuidTool "github.com/satori/go.uuid"
)

// StringInSlice :
func StringInSlice(a string, list []string) bool {
	for _, b := range list {
		if b == a {
			return true
		}
	}
	return false
}

// Error2String :
func Error2String(err error) string {
	return fmt.Sprintf("%v", err)
}

// Camel2Snake : camel case to snake case
func Camel2Snake(src string) string {
	searchFirstCap := regexp.MustCompile("(.)([A-Z][a-z]+)")
	searchAllCap := regexp.MustCompile("([a-z0-9])([A-Z])")
	snake := searchFirstCap.ReplaceAllString(src, "${1}_${2}")
	snake = searchAllCap.ReplaceAllString(snake, "${1}_${2}")
	return strings.ToLower(snake)
}

// RandSelector :
func RandSelector(listSrc *[]interface{}) interface{} {
	listSrcLen := len(*listSrc)
	currIndex := rand.Intn(listSrcLen)
	return (*listSrc)[currIndex]
}

// String2Int : transport string to int
func String2Int(param string) (int, error) {
	paramInt, err := strconv.Atoi(param)
	if err != nil {
		return 0, err
	}
	return paramInt, nil
}

// CostTime :
func CostTime(function, desc string, start time.Time) {
	duringTime := time.Now().Sub(start).Seconds() * 1000
	logging.Info("%v: %v, cost time is: %.2f ms", function, desc, duringTime)
}

// ErrorList2String :
func ErrorList2String(src []error) string {
	var retStrList []string
	for index := range src {
		errStr := fmt.Sprintf("%v", src[index])
		retStrList = append(retStrList, errStr)
	}
	return strings.Join(retStrList, ",")
}

// ListJoinWithString :
func ListJoinWithString(rawList *[]string, joinString string) string {
	return strings.Join((*rawList)[:], joinString)
}

// NewUUID : generate uuid
func NewUUID() string {
	uuid := uuidTool.NewV4()
	buf := make([]byte, 32)
	hex.Encode(buf[:], uuid[:])
	return string(buf[:])
}

// StringSplit : split a string
func StringSplit(src string, splitChar string) []string {
	if src == "" {
		return []string{}
	}
	return strings.Split(src, splitChar)
}
