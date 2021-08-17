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

package logging

import (
	"bcs-cc/config"
	"bcs-cc/storage"
	"fmt"
	"runtime"

	"github.com/golang/glog"
)

// Log level
const (
	InfoLevel  = 10
	WarnLevel  = 20
	ErrorLevel = 30
	FatalLevel = 40
)

var (
	level     = InfoLevel
	logConfig = config.GlobalConfigurations.Logging
)

// Init : init the log
func Init() error {
	logConfig = config.GlobalConfigurations.Logging
	glog.InitLogs(logConfig.FileDir, logConfig.MaxSize, logConfig.Stderr)
	switch logConfig.Level {
	case "info":
		level = InfoLevel
	case "warn":
		level = WarnLevel
	case "warning":
		level = WarnLevel
	case "error":
		level = ErrorLevel
	case "fatal":
		level = FatalLevel
	default:
		level = InfoLevel
	}

	return nil
}

// Close : close log
func Close() {
	glog.Flush()
}

// PushMsgToRedis : push message to redis
func PushMsgToRedis(message string, v ...interface{}) error {
	if config.GlobalConfigurations.DisableEncrypt {
		return nil
	}
	// push Redis
	redisConf := config.GlobalConfigurations.RedisConf
	redisClient := storage.GetDefaultRedisSession().Client
	return redisClient.RPush(redisConf.QueueName, message).Err()
}

func runtimeInfo() string {
	funcName, file, line, ok := runtime.Caller(2)
	if ok {
		return fmt.Sprintf("[%s] [%v] [%s] ", file, line, runtime.FuncForPC(funcName).Name())
	}
	return ""
}

// Info :
func Info(format string, v ...interface{}) {
	if level <= InfoLevel {
		if logConfig.LogToRedis {
			PushMsgToRedis(format, v...)
		}
		glog.Infof(runtimeInfo()+format, v...)
	}
}

// Warn :
func Warn(format string, v ...interface{}) {
	if level <= WarnLevel {
		if config.GlobalConfigurations.Logging.LogToRedis {
			PushMsgToRedis(format, v...)
		}
		glog.Warningf(runtimeInfo()+format, v...)
	}
}

// Warning :
func Warning(format string, v ...interface{}) {
	Warn(format, v...)
}

// Error :
func Error(format string, v ...interface{}) {
	if level <= ErrorLevel {
		if logConfig.LogToRedis {
			PushMsgToRedis(format, v...)
		}
		glog.Errorf(runtimeInfo()+format, v...)
	}
}

// Fatal :
func Fatal(format string, v ...interface{}) {
	if level <= ErrorLevel {
		if logConfig.LogToRedis {
			PushMsgToRedis(format, v...)
		}
		glog.Fatalf(runtimeInfo()+format, v...)
	}
}
