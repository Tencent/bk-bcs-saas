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

package com.tencent.devops.project.service.external

import com.fasterxml.jackson.databind.ObjectMapper
import com.tencent.devops.project.api.XBkAuthResourceApi
import com.tencent.devops.project.pojo.Result
import com.tencent.devops.project.pojo.user.UserVO
import okhttp3.MediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.security.cert.CertificateException
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

@Service
class UserService constructor(
    private val objectMapper: ObjectMapper,
    private val xBkAuthResourceApi: XBkAuthResourceApi
) {
    private val logger = LoggerFactory.getLogger(UserService::class.java)

    @Value("\${bk_login.path}")
    lateinit var path: String

    @Value("\${bk_login.getUser}")
    lateinit var getUser: String

    @Value("\${bk_login.bk_app_code}")
    lateinit var bkAppCode: String

    @Value("\${bk_login.bk_app_secret}")
    lateinit var bkAppSecret: String

    fun getStaffInfo(bkToken: String): UserVO {
        val userId = xBkAuthResourceApi.getBkUsername(bkToken)
        val url = (path + getUser)
        val map = HashMap<String, String>()
        map["bk_app_code"] = bkAppCode
        map["bk_app_secret"] = bkAppSecret
        map["bk_username"] = userId

        val mediaType = MediaType.parse("application/json")
        val json = objectMapper.writeValueAsString(map)
        logger.info("Get the user from url $url with body $json")
        val requestBody = RequestBody.create(mediaType, json)
        val httpReq = Request.Builder()
                .url(url)
                .post(requestBody)
                .build()

        val response = getUnsafeOkHttpClient().newCall(httpReq).execute()
        val responseContent = response.body()!!.string()
        if (!response.isSuccessful) {
            logger.error("CommitResourceApi $path$getUser fail.")
            throw RuntimeException("CommitResourceApi $path$getUser fail")
        }
        logger.info("Get the user response - $responseContent")
        val resultMap = objectMapper.readValue(responseContent, Result(LinkedHashMap<String, String>())::class.java)
        val data = resultMap.data
        val userVO = UserVO("", "", "", userId, "")
        if (data != null) {
            userVO.chinese_name = data["chname"] ?: ""
        }
        return userVO
    }

    private fun getUnsafeOkHttpClient(): OkHttpClient {
        try {
            // Create a trust manager that does not validate certificate chains
            val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
                @Throws(CertificateException::class)
                override fun checkClientTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {
                }

                @Throws(CertificateException::class)
                override fun checkServerTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {
                }

                override fun getAcceptedIssuers(): Array<java.security.cert.X509Certificate> {
                    return arrayOf()
                }
            })

            // Install the all-trusting trust manager
            val sslContext = SSLContext.getInstance("SSL")
            sslContext.init(null, trustAllCerts, java.security.SecureRandom())
            // Create an ssl socket factory with our all-trusting manager
            val sslSocketFactory = sslContext.socketFactory

            val builder = OkHttpClient.Builder()
            builder.sslSocketFactory(sslSocketFactory, trustAllCerts[0] as X509TrustManager)
            builder.hostnameVerifier { _, _ -> true }

            return builder.build()
        } catch (e: Exception) {
            throw RuntimeException(e)
        }
    }
}