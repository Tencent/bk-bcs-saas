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

package storage

// once synchronization
import (
	"sync"
)

// IDBSession : interface of db session
type IDBSession interface {
	Open() error
	Close()
}

// GLobals
var (
	GlobalSession      *DBSession
	GlobalRedisSession *RedisSession
)

var dbOnce sync.Once

// GetDefaultSession : init the db session pool
func GetDefaultSession() *DBSession {
	if GlobalSession == nil {
		dbOnce.Do(func() {
			GlobalSession = &DBSession{}
			err := GlobalSession.Open()
			if err != nil {
				panic(err)
			}
			// 先关闭
			// GlobalSession.DB.LogMode(true)
		})
	}
	return GlobalSession
}

var redisOnce sync.Once

// GetDefaultRedisSession : get default redis session for default database
func GetDefaultRedisSession() *RedisSession {
	if GlobalRedisSession == nil {
		redisOnce.Do(func() {
			GlobalRedisSession = &RedisSession{}
			err := GlobalRedisSession.Init()
			if err != nil {
				panic(err)
			}
		})
	}
	return GlobalRedisSession
}
