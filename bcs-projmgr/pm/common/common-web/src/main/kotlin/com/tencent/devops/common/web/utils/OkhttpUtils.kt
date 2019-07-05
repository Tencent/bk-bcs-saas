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

package com.tencent.devops.common.web.utils

import okhttp3.Request
import okhttp3.Response
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.TimeUnit

object OkhttpUtils {

    private val logger = LoggerFactory.getLogger(OkhttpUtils::class.java)

    val okHttpClient = okhttp3.OkHttpClient.Builder()
            .connectTimeout(60L, TimeUnit.SECONDS)
            .readTimeout(30L, TimeUnit.MINUTES)
            .writeTimeout(30L, TimeUnit.MINUTES)
            .build()!!

    fun doGet(url: String, headers: Map<String, String> = mapOf()): Response {
        val requestBuilder = Request.Builder()
                .url(url)
                .get()
        if (headers.isNotEmpty()) {
            headers.forEach { key, value ->
                requestBuilder.addHeader(key, value)
            }
        }
        val request = requestBuilder.build()
        return okHttpClient.newCall(request).execute()
    }

    fun doHttp(request: Request): Response {
        return okHttpClient.newCall(request).execute()
    }

    fun downloadFile(url: String, destPath: File) {
        val request = Request.Builder()
                .url(url)
                .get()
                .build()
        okHttpClient.newCall(request).execute().use { response ->
            if (response.code() == HttpStatus.NOT_FOUND.value()) {
                logger.warn("The file $url is not exist")
                throw RuntimeException("文件不存在")
            }
            if (!response.isSuccessful) {
                logger.warn("fail to download the file from $url because of ${response.message()} and code ${response.code()}")
                throw RuntimeException("获取文件失败")
            }
            if (!destPath.parentFile.exists()) destPath.parentFile.mkdirs()
            val buf = ByteArray(4096)
            response.body()!!.byteStream().use { bs ->
                var len = bs.read(buf)
                FileOutputStream(destPath).use { fos ->
                    while (len != -1) {
                        fos.write(buf, 0, len)
                        len = bs.read(buf)
                    }
                }
            }
        }
    }

    fun downloadFile(response: Response, destPath: File) {
        if (response.code() == HttpStatus.NOT_MODIFIED.value()) {
            logger.info("file is newest, do not download to $destPath")
            return
        }
        if (!response.isSuccessful) {
            logger.warn("fail to download the file because of ${response.message()} and code ${response.code()}")
            throw RuntimeException("获取文件失败")
        }
        if (!destPath.parentFile.exists()) destPath.parentFile.mkdirs()
        val buf = ByteArray(4096)
        response.body()!!.byteStream().use { bs ->
            var len = bs.read(buf)
            FileOutputStream(destPath).use { fos ->
                while (len != -1) {
                    fos.write(buf, 0, len)
                    len = bs.read(buf)
                }
            }
        }
    }
}