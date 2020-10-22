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

package com.tencent.devops.project.api

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import com.tencent.devops.common.api.exception.CustomException
import com.tencent.devops.project.api.pojo.*
import okhttp3.MediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component
import java.security.cert.CertificateException
import java.security.cert.X509Certificate
import java.util.concurrent.TimeUnit
import javax.net.ssl.*
import javax.ws.rs.core.Response

@Component
class XBkAuthResourceApi @Autowired constructor(
        private val objectMapper: ObjectMapper
) {
    private val okHttpClient = okhttp3.OkHttpClient.Builder()
            .connectTimeout(5L, TimeUnit.SECONDS)
            .readTimeout(60L, TimeUnit.SECONDS)
            .writeTimeout(60L, TimeUnit.SECONDS)
            .build()

    @Value("\${auth.url}")
    private lateinit var url: String

    @Value("\${auth.xBkAppCode}")
    private lateinit var xBkAppCode: String

    @Value("\${auth.xBkAppSecret}")
    private lateinit var xBkAppSecret: String

    @Value("\${bk_login.url}")
    private lateinit var bkUrl: String

    fun createResource(
            systemCode: XBkAuthSystemCode,
            creatorType: String,
            creatorId: String,
            scopeType: XBkAuthScopeType,
            scopeId: String,
            resourceType: XBkAuthResourceType,
            resourceId: String,
            resourceName: String
    ) {
        val url = "$url/bkiam/api/v1/perm/systems/${systemCode.value}/resources/batch-register"
        logger.info("createResource url=$url")
        val xBkAuthResourceCreateResources = mutableSetOf(XBkAuthResourceCreateRequest.Resource(
                resourceId = mutableSetOf(XBkAuthResourceCreateRequest.ResourceId(
                        resourceId = resourceId,
                        resourceType = resourceType.value
                )),
                resourceName = resourceName,
                resourceType = resourceType.value,
                scopeId = scopeId,
                scopeType = scopeType.value
        ))
        val xBkAuthResourceCreateRequest = XBkAuthResourceCreateRequest(
                creatorId,
                creatorType,
                xBkAuthResourceCreateResources
        )
        val content = objectMapper.writeValueAsString(xBkAuthResourceCreateRequest)
        logger.info("createResource  body content=$content")
        val mediaType = MediaType.parse("application/json; charset=utf-8")
        val requestBody = RequestBody.create(mediaType, content)
        val request = Request.Builder().url(url)
                .header("X-BK-APP-CODE", "$xBkAppCode")
                .header("X-BK-APP-SECRET", "$xBkAppSecret")
                .post(requestBody)
                .build()
        val httpClient = okHttpClient.newBuilder().build()
        httpClient.newCall(request).execute().use { response ->
            val responseContent = response.body()!!.string()
            logger.info("Auth create resource response: $responseContent")
            if (!response.isSuccessful) {
                logger.error("Fail to create auth resource. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Fail to create auth resource")
            }

            val responseObject = objectMapper.readValue<XBkAuthResourceCreateResponse>(responseContent)
            if (!responseObject.result) {
                logger.error("Fail to create auth resource. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, responseObject.bk_error_msg)
            }
        }
    }

    fun modifyResource(
            systemCode: XBkAuthSystemCode,
            scopeType: XBkAuthScopeType,
            scopeId: String,
            resourceType: XBkAuthResourceType,
            resourceId: String,
            resourceName: String
    ) {
        val url = "$url/bkiam/api/v1/perm/systems/${systemCode.value}/resources"

        logger.info("Auth modify resource url: $url")
        val xBkAuthResourceModifyRequest = XBkAuthResourceModifyRequest(
                scopeType = scopeType.value,
                scopeId = scopeId,
                resourceName = resourceName,
                resourceType = resourceType.value,
                resourceId = setOf(XBkAuthResourceModifyRequest.ResourceId(
                        resourceId = resourceId,
                        resourceType = resourceType.value
                ))
        )
        val content = objectMapper.writeValueAsString(xBkAuthResourceModifyRequest)
        logger.info("Auth modify resource content: $content")
        val mediaType = MediaType.parse("application/json; charset=utf-8")
        val requestBody = RequestBody.create(mediaType, content)
        val request = Request.Builder().url(url)
                .header("X-BK-APP-CODE", "$xBkAppCode")
                .header("X-BK-APP-SECRET", "$xBkAppSecret")
                .put(requestBody)
                .build()
        val httpClient = okHttpClient.newBuilder().build()
        httpClient.newCall(request).execute().use { response ->
            val responseContent = response.body()!!.string()
            logger.info("Auth modify resource response: $responseContent")
            if (!response.isSuccessful) {
                logger.error("Fail to modify auth resource. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Fail to modify auth resource")
            }

            val responseObject = objectMapper.readValue<XBkAuthResourceModifyResponse>(responseContent)
            if (!responseObject.result) {
                logger.error("Fail to modify auth resource. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, responseObject.bk_error_msg)
            }
        }
    }

    fun deleteResource(
            systemCode: XBkAuthSystemCode,
            scopeType: XBkAuthScopeType,
            scopeId: String,
            resourceType: XBkAuthResourceType,
            resourceId: String
    ) {
        val url = "$url/bkiam/api/v1/perm/systems/${systemCode.value}/resources/batch-delete"
        val xBkAuthResourceDeleteRequest = XBkAuthResourceDeleteRequest(
                listOf(XBkAuthResourceDeleteRequest.Resource(
                        scopeType = scopeType.value,
                        scopeId = scopeId,
                        resourceType = resourceType.value,
                        resourceId = setOf(XBkAuthResourceDeleteRequest.ResourceId(
                                resourceId = resourceId,
                                resourceType = resourceType.value
                        ))
                ))

        )
        val content = objectMapper.writeValueAsString(xBkAuthResourceDeleteRequest)
        val mediaType = MediaType.parse("application/json; charset=utf-8")
        val requestBody = RequestBody.create(mediaType, content)
        val request = Request.Builder().url(url)
                .header("X-BK-APP-CODE", "$xBkAppCode")
                .header("X-BK-APP-SECRET", "$xBkAppSecret")
                .delete(requestBody)
                .build()
        val httpClient = okHttpClient.newBuilder().build()
        httpClient.newCall(request).execute().use { response ->
            val responseContent = response.body()!!.string()
            logger.info("Auth delete resource response: $responseContent")
            if (!response.isSuccessful) {
                logger.error("Fail to delete auth resource. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Fail to delete auth resource")
            }

            val responseObject = objectMapper.readValue<XBkAuthResourceDeleteResponse>(responseContent)
            if (!responseObject.result) {
                logger.error("Fail to delete auth resource. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, responseObject.bk_error_msg)
            }
        }
    }

    fun getUserAuthorizedScopes(userId: String): XBkAuthorizedScopesResponse<List<String>> {
        val url = "$url/bkiam/api/v1/perm/scope_type/project/authorized-scopes/"
        val map = mapOf<String, String>("principal_type" to "user", "principal_id" to userId)

        val content = objectMapper.writeValueAsString(map)
        val mediaType = MediaType.parse("application/json; charset=utf-8")
        val requestBody = RequestBody.create(mediaType, content)
        val request = Request.Builder().url(url)
                .header("X-BK-APP-CODE", "$xBkAppCode")
                .header("X-BK-APP-SECRET", "$xBkAppSecret")
                .post(requestBody)
                .build()
        val httpClient = okHttpClient.newBuilder().build()
        logger.info("Start to get the user auth scope by user ($userId) with url ($url)")
        httpClient.newCall(request).execute().use { response ->
            val responseContent = response.body()!!.string()
            if (!response.isSuccessful) {
                logger.error("Fail to get project users. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Fail to get project users")
            }

            val responseObject = objectMapper.readValue<XBkAuthorizedScopesResponse<List<String>>>(responseContent)
            if (!responseObject.result) {
                logger.error("Fail to delete auth resource. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, responseObject.bk_error_msg)
            }
            return responseObject
        }
    }

    fun getAccessToken(bkToken: String): String {
        val url = "$url/bkiam/api/v1/auth/access-tokens"
        logger.info("The url to get access_token is url: ($url) ")
        val accessTokenRequest = mapOf(
                "id_provider" to "bk_login",
                "grant_type" to "authorization_code",
                "bk_token" to bkToken
        )
        logger.info(accessTokenRequest.toString())
        val content = objectMapper.writeValueAsString(accessTokenRequest)
        val mediaType = MediaType.parse("application/json; charset=utf-8")
        val requestBody = RequestBody.create(mediaType, content)
        val request = Request.Builder().url(url)
                .header("X-BK-APP-CODE", "$xBkAppCode")
                .header("X-BK-APP-SECRET", "$xBkAppSecret")
                .post(requestBody)
                .build()

        var accessToken = ""
        val httpClient = okHttpClient.newBuilder().build()
        httpClient.newCall(request).execute().use { response ->
            val responseContent = response.body()!!.string()
            logger.info("Get accessToken response: $responseContent")
            if (!response.isSuccessful) {
                logger.error("Get accessToken response: $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Fail to get access_token")
            }

            val responseObject = objectMapper.readValue<Map<String, Any>>(responseContent)
            if (!(responseObject["result"] as Boolean)) {
                logger.error("Fail to create get accessToken. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Fail to create get accessToken")
            }
            val responseData: Map<String, String> = responseObject["data"] as Map<String, String>
            if (responseData["access_token"].isNullOrEmpty()) {
                logger.error("Fail to get accessToken. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Fail to get accessToken")
            }

            accessToken = responseData["access_token"] as String
        }
        return accessToken
    }

    fun getBkUsername(bkToken: String): String {
        val url = "$bkUrl/login/api/v2/is_login/?bk_token=$bkToken"
        logger.info("Get bk_username url: $url")

        val request = Request.Builder().url(url).get()
                .build()
        val client = getUnsafeOkHttpClient()
        client.newCall(request).execute().use { response ->
            val responseBody = response.body()!!.string()
            logger.info("Get bk_username responseBody: $responseBody")
            if (!response.isSuccessful) {
                logger.error("failed to get bk_username responseBody: $responseBody")
                // 验证失败后，401返回
                throw CustomException(Response.Status.UNAUTHORIZED, "failed to get bk_username responseBody: $responseBody")
            }

            val responseData: Map<String, Any> = jacksonObjectMapper().readValue(responseBody)
            val code = responseData["bk_error_code"] as Int
            if (code != 0) {
                logger.error("failed to get bk_username responseBody: $responseBody")
                // 验证失败后，401返回
                throw CustomException(Response.Status.UNAUTHORIZED, "Fail to get accessToken")
            }
            val responseDataData = responseData["data"] as Map<String, String>

            return responseDataData["bk_username"] as String
        }
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
            val sslSocketFactory = sslContext.getSocketFactory()

            val builder = OkHttpClient.Builder()
            builder.sslSocketFactory(sslSocketFactory, trustAllCerts[0] as X509TrustManager)
            builder.hostnameVerifier(object : HostnameVerifier {
                override fun verify(hostname: String, session: SSLSession): Boolean {
                    return true
                }
            })

            val okHttpClient = builder.build()
            return okHttpClient
        } catch (e: Exception) {
            throw RuntimeException(e)
        }
    }

    companion object {
        private val logger = LoggerFactory.getLogger(XBkAuthResourceApi::class.java)
    }
}