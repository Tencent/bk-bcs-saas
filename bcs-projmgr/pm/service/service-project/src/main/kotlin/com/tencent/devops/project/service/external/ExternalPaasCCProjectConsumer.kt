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
import com.fasterxml.jackson.module.kotlin.readValue
import com.tencent.devops.common.api.exception.OperationException
import com.tencent.devops.project.pojo.*
import com.tencent.devops.project.pojo.tof.Response
import okhttp3.MediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.util.concurrent.TimeUnit

/**
 * 外部版，去掉rabbitmq
 */
@Service
class ExternalPaasCCProjectConsumer @Autowired constructor(
        private val objectMapper: ObjectMapper
) {
    private val okHttpClient: OkHttpClient = okhttp3.OkHttpClient.Builder()
            .connectTimeout(5L, TimeUnit.SECONDS)
            .readTimeout(300L, TimeUnit.SECONDS)
            .writeTimeout(60L, TimeUnit.SECONDS)
            .build()

    @Value("\${bcs_cc.externalUrl}")
    private lateinit var ccUrl: String

    fun onRecvProjectCreateMessage(paasCCCreateProject: PaasCCCreateProject) {
        createPaasCCProject(paasCCCreateProject.userId,
                paasCCCreateProject.accessToken,
                paasCCCreateProject.projectCreateInfo,
                paasCCCreateProject.projectId)
    }

    fun onRecvProjectUpdateMessage(paasCCUpdateProject: PaasCCUpdateProject) {

        updatePaasCCProject(paasCCUpdateProject.userId,
                paasCCUpdateProject.accessToken,
                paasCCUpdateProject.projectUpdateInfo,
                paasCCUpdateProject.projectId)
    }

    fun onRecvProjectLogoUpdateMessage(paasCCUpdateProjectLogo: PaasCCUpdateProjectLogo) {
        updatePaasCCProjectLogo(paasCCUpdateProjectLogo.userId,
                paasCCUpdateProjectLogo.accessToken,
                paasCCUpdateProjectLogo.projectUpdateLogoInfo,
                paasCCUpdateProjectLogo.projectId)
    }

    fun createPaasCCProject(
            userId: String,
            accessToken: String,
            projectCreateInfo: ProjectCreateInfo,
            projectId: String
    ) {
        logger.info("Create the paas cc project $projectCreateInfo by user $userId with token $accessToken")
        val paasCCProject = PaasCCProjectForCreate(
                projectCreateInfo.project_name,
                projectCreateInfo.english_name,
                projectCreateInfo.project_type,
                projectCreateInfo.description,
                projectCreateInfo.bg_id,
                projectCreateInfo.bg_name,
                projectCreateInfo.dept_id,
                projectCreateInfo.dept_name,
                projectCreateInfo.center_id,
                projectCreateInfo.center_name,
                projectCreateInfo.is_secrecy,
                projectCreateInfo.kind,
                projectId,
                userId
        )

        val url = "$ccUrl?access_token=$accessToken"
        val mediaType = MediaType.parse("application/json; charset=utf-8")
        val param = objectMapper.writeValueAsString(paasCCProject)
        val requestBody = RequestBody.create(mediaType, param)
        val request = Request.Builder().url(url).post(requestBody).build()
        val responseContent = request(request, "Failed to call PaasCC api to create a project.")
        val result = objectMapper.readValue<Result<Map<String, Any>>>(responseContent)
        if (result.isNotOk()) {
            logger.warn("Fail to create the projects in paas cc with response $responseContent")
            throw OperationException("Failed to synchronization project info to PaasCC")
        }
    }

    fun updatePaasCCProject(
            userId: String,
            accessToken: String,
            projectUpdateInfo: ProjectUpdateInfo,
            projectId: String
    ) {
        logger.info("Update the paas cc project $projectUpdateInfo by user $userId with token $accessToken")

        val paasCCProjectForUpdate = PaasCCProjectForUpdate(
                projectUpdateInfo.project_name,
                projectUpdateInfo.english_name,
                projectUpdateInfo.project_type,
                projectUpdateInfo.bg_id,
                projectUpdateInfo.bg_name,
                projectUpdateInfo.center_id,
                projectUpdateInfo.center_name,
                projectUpdateInfo.dept_id,
                projectUpdateInfo.dept_name,
                projectUpdateInfo.description,
                projectUpdateInfo.english_name,
                userId
        )

        val url = "$ccUrl/$projectId?access_token=$accessToken"
        val mediaType = MediaType.parse("application/json; charset=utf-8")
        val param = objectMapper.writeValueAsString(paasCCProjectForUpdate)
        val requestBody = RequestBody.create(mediaType, param)
        val request = Request.Builder().url(url).put(requestBody).build()
        val responseContent = request(request, "Failed to call PaasCC api to update a project info.")
        logger.info("Success to update the project with response $responseContent")
        val result: Response<Any> = objectMapper.readValue(responseContent)

        if (result.code.toInt() != 0) {
            logger.warn("Fail to update the project in paas cc with response $responseContent")
            throw OperationException("Failed to update project info to PaasCC")
        }
    }

    fun updatePaasCCProjectLogo(
            userId: String,
            accessToken: String,
            projectUpdateLogoInfo: ProjectUpdateLogoInfo,
            projectId: String
    ) {
        logger.info("Update the paas cc projectLogo $projectUpdateLogoInfo by user $userId with token $accessToken")

        val url = "$ccUrl/$projectId?access_token=$accessToken"
        val mediaType = MediaType.parse("application/json; charset=utf-8")
        val param = objectMapper.writeValueAsString(projectUpdateLogoInfo)
        val requestBody = RequestBody.create(mediaType, param)
        val request = Request.Builder().url(url).put(requestBody).build()
        val responseContent = request(request, "Failed to call PaasCC api to update a project logo.")
        logger.info("Success to update the projectLogo with response $responseContent")
        val result: Response<Any> = objectMapper.readValue(responseContent)

        if (result.code.toInt() != 0) {
            logger.warn("Fail to update the projectLogo in paas cc with response $responseContent")
            throw OperationException("Failed to update project logo to PaasCC")
        }
    }

    private fun request(request: Request, errorMessage: String): String {
        val httpClient = okHttpClient.newBuilder().build()

        httpClient.newCall(request).execute().use { response ->
            val responseContent = response.body()!!.string()
            if (!response.isSuccessful) {
                logger.warn("Fail to request($request) with code ${response.code()} , message ${response.message()} and response $responseContent")
                throw OperationException(errorMessage)
            }
            return responseContent
        }
    }

    companion object {
        private val logger = LoggerFactory.getLogger(ExternalPaasCCProjectConsumer::class.java)
    }
}