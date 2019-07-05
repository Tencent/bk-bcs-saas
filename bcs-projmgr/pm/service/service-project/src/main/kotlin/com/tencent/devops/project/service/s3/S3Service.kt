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

package com.tencent.devops.project.service.s3

import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.client.builder.AwsClientBuilder
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder
import com.amazonaws.services.s3.model.CannedAccessControlList
import com.amazonaws.services.s3.model.PutObjectRequest
import com.tencent.devops.common.api.exception.OperationException
import com.tencent.devops.common.service.Profile
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service
import java.io.File
import java.lang.RuntimeException

@Service
class S3Service @Autowired constructor(private val profile: Profile) {

    @Value("\${s3.endpointUrl:#{null}}")
    private val endpointUrl: String? = null

    @Value("\${s3.accessKey:#{null}}")
    private val accessKey: String? = null

    @Value("\${s3.secretKey:#{null}}")
    private val secretKey: String? = null

    @Value("\${s3.bucketName:#{null}}")
    private val bucketName: String? = null

    private var client: AmazonS3? = null

    fun saveLogo(logo: File, projectCode: String): String {
        validate()
        val key = logoKey(projectCode)
        val request = PutObjectRequest(bucketName, key, logo)
            .withCannedAcl(CannedAccessControlList.PublicRead)
        try {
            val client = awsClient()
            client.putObject(request)
            return client.getUrl(bucketName, key).toString() + "?v=${System.currentTimeMillis() / 1000}"
        } catch (e: Exception) {
            logger.warn("Fail to save the logo of project $projectCode", e)
            throw OperationException("保存项目Logo失败")
        }
    }

    private fun logoKey(projectCode: String): String {
        return "${profile.getEnv().name.toLowerCase()}/logo/default_$projectCode.png"
    }

    private fun awsClient(): AmazonS3 {
        if (client == null) {
            synchronized(this) {
                if (client == null) {
                    val credentials = BasicAWSCredentials(accessKey, secretKey)

                    client = AmazonS3ClientBuilder.standard()
                        .withCredentials(AWSStaticCredentialsProvider(credentials))
                        .withEndpointConfiguration(
                            AwsClientBuilder.EndpointConfiguration(
                                "http://bk.com",
                                ""
                            )
                        )
                        .build()
                }
            }
        }
        return client!!
    }

    private fun validate() {
        if (endpointUrl.isNullOrBlank()) {
            throw RuntimeException("S3 endpoint url is empty")
        }
        if (accessKey.isNullOrBlank()) {
            throw RuntimeException("S3 access key is empty")
        }
        if (secretKey.isNullOrBlank()) {
            throw RuntimeException("S3 secret key is empty")
        }
    }

    companion object {
        private val logger = LoggerFactory.getLogger(S3Service::class.java)
    }
}
