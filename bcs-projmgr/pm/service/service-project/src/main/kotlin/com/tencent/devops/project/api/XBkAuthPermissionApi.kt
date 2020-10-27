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
import com.tencent.devops.common.api.exception.RemoteServiceException
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
import java.util.concurrent.TimeUnit
import javax.net.ssl.*
import javax.ws.rs.core.Response

@Component
class XBkAuthPermissionApi @Autowired constructor(
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


    // 批量查询有权限的资源,若返回的map的Entry中Boolean为true，则表明用户对该资源拥有所有权限
    fun getUserResourcesByPermissions(
            userId: String,
            userType: String,
            scopeType: XBkAuthScopeType,
            resourceType: XBkAuthResourceType,
            permissions: Set<XBkAuthPermission>,
            systemCode: XBkAuthSystemCode,
            supplier: (() -> List<String>)?
    ): Map<XBkAuthPermission, List<String>> {

        val url = "$url/bkiam/api/v1/perm/systems/${systemCode.value}/authorized-resources/search"
        logger.info("getUserResourcesByPermissions url=$url")
        val resultMap = LinkedHashMap<XBkAuthPermission, List<String>>()

        val requestBean = XBkUserResourcesAuthRequest(
                principalId = userId,
                principalType = userType,
                scopeType = scopeType.value,
                scopeId = systemCode.value,
                resourceTypesActions = permissions.map {
                    XBkUserResourcesAuthRequest.ResourceTypesAction(
                            it.value,
                            resourceType.value
                    )
                },
                resourceDataType = "array",
                exactResource = true
        )


        val content = objectMapper.writeValueAsString(requestBean)
        logger.info("getUserResourcesByPermissions content=$content")
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
            logger.info("Auth get user resources by permissions response: $responseContent")
            if (!response.isSuccessful) {
                logger.error("Fail to create auth resource. $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Fail to get user resources by permissions")
            }

            val responseObject = objectMapper.readValue<XBkUserResourcesAuthResponse>(responseContent)
            if (!responseObject.result) {
                logger.error("Fail to get user resources by permissions . $responseContent")
                throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, responseObject.message!!)
            } else {
                try {
                    responseObject.data!!.forEach { reqData ->
                        putData(reqData, resultMap)
                    }
                    return resultMap
                } catch (ignored: Exception) {
                    logger.error("bkiam, An exception occurs in the parse response bean, msg: $ignored")
                    throw RemoteServiceException("bkiam, An exception occurs in the parse response bean, msg: $ignored")
                }
            }
        }
    }

    private fun putData(
            reqData: XBkUserResourcesAuthResponse.Data,
            resultMap: LinkedHashMap<XBkAuthPermission, List<String>>
    ) {
        val resourceIds = reqData.resourceIds
        val bkAuthPermission = XBkAuthPermission.get(reqData.actionId)

        if (resourceIds.isEmpty()) {
            resultMap[bkAuthPermission] = emptyList()
        } else {
            val resources = mutableSetOf<String>()
            resourceIds.forEach { resourceId ->
                resourceId!!.forEach { resourceIdMap ->
                    resources.add(resourceIdMap!!["resource_id"] ?: "")
                }
            }

            resultMap[bkAuthPermission] = resources.toList()
        }
    }

    companion object {
        private val logger = LoggerFactory.getLogger(XBkAuthPermissionApi::class.java)
    }
}