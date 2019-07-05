/*
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 *
 */

package com.tencent.devops.common.api.util

import java.text.SimpleDateFormat
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.ZoneOffset
import java.util.Calendar
import java.util.Date

fun LocalDateTime.timestamp(): Long {
    val zoneId = ZoneId.systemDefault()
    return this.atZone(zoneId).toInstant().epochSecond
}

fun LocalDateTime.timestampmilli(): Long {
    val zoneId = ZoneId.systemDefault()
    return this.atZone(zoneId).toInstant().toEpochMilli()
}

object DateTimeUtil {
    /**
     * 获取从当前开始一定单位时间间隔的日期
     * @param unit 单位 Calendar.SECONDS
     * @param timeSpan 实际间隔
     * @return 日期类实例
     */
    fun getFutureDateFromNow(unit: Int, timeSpan: Int): Date {
        val cd = Calendar.getInstance()
        cd.time = Date()
        cd.add(unit, timeSpan)
        return cd.time
    }

    /**
     * 按指定日期时间格式格式化日期时间
     * @param date 日期时间
     * @param format 格式化字符串
     * @return 字符串
     */
    fun formatDate(date: Date, format: String = "yyyy-MM-dd HH:mm:ss"): String {
        val simpleDateFormat = SimpleDateFormat(format)
        return simpleDateFormat.format(date)
    }

    fun convertLocalDateTimeToTimestamp(localDateTime: LocalDateTime?): Long {
        return localDateTime?.toEpochSecond(ZoneOffset.ofHours(8)) ?: 0L
    }

    fun toDateTime(dateTime: LocalDateTime?, format: String = "yyyy-MM-dd HH:mm:ss"): String {
        if (dateTime == null) {
            return ""
        }
        val zone = ZoneId.systemDefault()
        val instant = dateTime.atZone(zone).toInstant()
        val simpleDateFormat = SimpleDateFormat(format)
        return simpleDateFormat.format(Date.from(instant))
    }

    /**
     * 毫秒时间
     * Long类型时间转换成视频时长
     */
    fun formatTime(timeStr: String): String {
        val time = timeStr.toLong() * 1000
        val hour = time / (60 * 60 * 1000)
        val minute = (time - hour * 60 * 60 * 1000) / (60 * 1000)
        val second = (time - hour * 60 * 60 * 1000 - minute * 60 * 1000) / 1000
        return (if (hour == 0L) "00" else if (hour >= 10) hour.toString() else "0$hour").toString() + "时" +
                (if (minute == 0L) "00" else if (minute >= 10) minute else "0$minute") + "分" +
                (if (second == 0L) "00" else if (second >= 10) second.toShort() else "0$second") + "秒"
    }
}