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

package com.tencent.devops.common.client

import com.fasterxml.jackson.databind.ObjectMapper
import com.tencent.devops.common.api.annotation.ServiceInterface
import com.tencent.devops.common.api.exception.ClientException
import com.tencent.devops.common.client.pojo.EnvProperties
import feign.Feign
import feign.Request
import feign.RetryableException
import feign.Retryer
import feign.jackson.JacksonDecoder
import feign.jackson.JacksonEncoder
import feign.jaxrs.JAXRSContract
import feign.okhttp.OkHttpClient
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.cloud.client.ServiceInstance
import org.springframework.cloud.consul.discovery.ConsulDiscoveryClient
import org.springframework.core.annotation.AnnotationUtils
import org.springframework.stereotype.Component
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.TimeUnit
import kotlin.reflect.KClass

@Component
class Client @Autowired constructor(
    private val consulClient: ConsulDiscoveryClient?,
    private val clientErrorDecoder: ClientErrorDecoder,
    private val envProperties: EnvProperties,
    objectMapper: ObjectMapper
) {

    private val interfaces = ConcurrentHashMap<KClass<*>, String>()
    private val okHttpClient = okhttp3.OkHttpClient.Builder()
        .connectTimeout(5L, TimeUnit.SECONDS)
        .readTimeout(60L, TimeUnit.SECONDS)
        .writeTimeout(60L, TimeUnit.SECONDS)
        .build()

    private val longRunClient = OkHttpClient(
        okhttp3.OkHttpClient.Builder()
            .connectTimeout(10L, TimeUnit.SECONDS)
            .readTimeout(30L, TimeUnit.MINUTES)
            .writeTimeout(30L, TimeUnit.MINUTES)
            .build()
    )

    private val feignClient = OkHttpClient(okHttpClient)
    private val jaxRsContract = JAXRSContract()
    private val jacksonDecoder = JacksonDecoder(objectMapper)
    private val jacksonEncoder = JacksonEncoder(objectMapper)

    @Value("\${spring.cloud.consul.discovery.tags:#{null}}")
    private val tag: String? = null

    @Value("\${scm.ip:#{null}}")
    private val scmIp: String? = null

    private val scmIpList = ArrayList<String>()

    private var hasParseScmIp = false

    private fun parseScmIp() {
        if (hasParseScmIp) {
            return
        }
        synchronized(scmIpList, {
            if (hasParseScmIp) {
                return
            }
            if (scmIp.isNullOrEmpty()) {
                logger.warn("The scm ip is empty")
            } else {
                scmIp!!.split(",").forEach {
                    val ip = it.trim()
                    if (ip.isEmpty()) {
                        logger.warn("Contain blank scm ip in configuration")
                        return@forEach
                    }
                    logger.info("Adding the scm ip($ip)")
                    scmIpList.add(ip)
                }
            }
            hasParseScmIp = true
        })
    }

    init {
    }

    fun <T : Any> get(clz: KClass<T>): T {
        val serviceName = findServiceName(clz)
        val serviceInstance = choose(serviceName)
        return Feign.builder()
            .client(feignClient)
            .errorDecoder(clientErrorDecoder)
            .encoder(jacksonEncoder)
            .decoder(jacksonDecoder)
            .contract(jaxRsContract)
            .target(
                clz.java,
                "${if (serviceInstance.isSecure) "https" else "http"}://${serviceInstance.host}:${serviceInstance.port}/api"
            )
        // .target(clz.java, "${if (serviceInstance.isSecure) "https" else "http"}://localhost:${serviceInstance.port}/api")
    }

    fun <T : Any> getWithoutRetry(clz: KClass<T>): T {
        val serviceName = findServiceName(clz)
        val serviceInstance = choose(serviceName)
        return Feign.builder()
            .client(longRunClient)
            .errorDecoder(clientErrorDecoder)
            .encoder(jacksonEncoder)
            .decoder(jacksonDecoder)
            .contract(jaxRsContract)
            .options(Request.Options(10 * 1000, 30 * 60 * 1000))
            .retryer(object : Retryer {
                override fun clone(): Retryer {
                    return this
                }

                override fun continueOrPropagate(e: RetryableException) {
                    throw e
                }
            })
            .target(
                clz.java,
                "${if (serviceInstance.isSecure) "https" else "http"}://${serviceInstance.host}:${serviceInstance.port}/api"
            )
    }

    /**
     * 通过网关访问微服务接口
     *
     */
    fun <T : Any> getGateway(clz: KClass<T>): T {
        val serviceName = findServiceName(clz)
        return Feign.builder()
            .client(feignClient)
            .errorDecoder(clientErrorDecoder)
            .encoder(jacksonEncoder)
            .decoder(jacksonDecoder)
            .contract(jaxRsContract)
            .target(clz.java, "http://${envProperties.gatewayUrl}/$serviceName/api")
    }

    // devnet区域的，只能直接通过ip访问
    fun <T : Any> getScm(clz: KClass<T>): T {
        val ip = chooseScm()
        return Feign.builder()
            .client(feignClient)
            .errorDecoder(clientErrorDecoder)
            .encoder(jacksonEncoder)
            .decoder(jacksonDecoder)
            .contract(jaxRsContract)
            .target(clz.java, "http://$ip/api")
    }

    private fun choose(serviceName: String): ServiceInstance {
        val instances =
            consulClient!!.getInstances(serviceName) ?: throw ClientException("找不到任何有效的\"$serviceName\"服务提供者")
        if (instances.isEmpty()) {
            throw ClientException("找不到任何有效的\"$serviceName\"服务提供者")
        }

        val matchTagInstances = ArrayList<ServiceInstance>()

        instances.forEach {
            if (it.metadata.isEmpty())
                return@forEach
            if (it.metadata.values.contains(tag)) {
                matchTagInstances.add(it)
            }
        }

        if (matchTagInstances.isEmpty()) {
            throw ClientException("找不到任何有效的\"$serviceName\"服务提供者")
        }
        if (matchTagInstances.size > 1) {
            matchTagInstances.shuffle()
        }
        return matchTagInstances[0]
    }

    private fun chooseScm(): String {
        parseScmIp()
        if (scmIpList.isEmpty()) {
            throw RuntimeException("The scm ip($scmIp) is not config")
        }

        val copy = ArrayList(scmIpList)
        copy.shuffle()
        return copy[0]
    }

    private fun findServiceName(clz: KClass<*>): String {
        return interfaces.getOrPut(clz, {
            val serviceInterface = AnnotationUtils.findAnnotation(clz.java, ServiceInterface::class.java)
            if (serviceInterface != null) {
                serviceInterface.value
            } else {
                val packageName = clz.qualifiedName.toString()
                val regex = Regex("""com.tencent.devops.([a-z]+).api.([a-zA-Z]+)""")
                val matches = regex.find(packageName) ?: throw ClientException("无法根据接口\"$packageName\"分析所属的服务")
                matches.groupValues[1]
            }
        })
    }

    companion object {
        private val logger = LoggerFactory.getLogger(Client::class.java)
    }
}
