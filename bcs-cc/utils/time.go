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
	"time"
)

var (
	// TimeLocation :
	TimeLocation *time.Location
)

// SetupTimeLocation : setup time location from string
func SetupTimeLocation(location string) error {
	var err error
	TimeLocation, err = time.LoadLocation(location)
	return err
}

// LocationNow : return now time in system location
func LocationNow() time.Time {
	now := time.Now()
	return now.In(TimeLocation)
}

// LocationTime : return time in system location
func LocationTime(t time.Time) time.Time {
	return t.In(TimeLocation)
}

// GetDurationBySeconds :
func GetDurationBySeconds(seconds int) time.Duration {
	return time.Duration(seconds) * time.Second
}

// TimeToISO8601 : time to iso8601 string
func TimeToISO8601(t time.Time) string {
	return t.Format("2006-01-02T15:04:05-0700")
}

// TimeFromISO8601 : time parse from iso8601 string
func TimeFromISO8601(t string) (time.Time, error) {
	return time.Parse("2006-01-02T15:04:05-0700", t)
}
