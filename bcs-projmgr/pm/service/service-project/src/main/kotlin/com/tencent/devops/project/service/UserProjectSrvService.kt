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

package com.tencent.devops.project.service

import com.tencent.devops.common.service.gray.Gray
import com.tencent.devops.model.project.tables.records.TServiceRecord
import com.tencent.devops.project.api.XBkAuthResourceApi
import com.tencent.devops.project.dao.FavoriteDao
import com.tencent.devops.project.dao.GrayTestDao
import com.tencent.devops.project.dao.ServiceDao
import com.tencent.devops.project.dao.ServiceTypeDao
import com.tencent.devops.project.pojo.Result
import com.tencent.devops.project.pojo.service.*
import org.jooq.DSLContext
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.data.redis.core.RedisTemplate
import org.springframework.stereotype.Service

@Service
class UserProjectSrvService @Autowired constructor(
    private val dslContext: DSLContext,
    private val serviceTypeDao: ServiceTypeDao,
    private val serviceDao: ServiceDao,
    private val grayTestDao: GrayTestDao,
    private val favoriteDao: FavoriteDao,
    private val gray: Gray,
    private val redisTemplate: RedisTemplate<String, String>,
    private val xBkAuthResourceApi: XBkAuthResourceApi
) {

    /**
     * 修改服务关注
     */
    fun updateCollected(bk_token: String, service_id: Long, collector: Boolean): Result<Boolean> {
        val userId = xBkAuthResourceApi.getBkUsername(bk_token)
        if (collector) {
            if (favoriteDao.create(dslContext, userId, service_id) > 0) {
                return Result(0, "服务收藏成功", "", true)
            }
        } else {
            if (favoriteDao.delete(dslContext, userId, service_id) > 0) {
                return Result(0, "服务取消收藏成功", "", true)
            }
        }
        return Result(false)
    }

    fun listService(bk_token: String, projectId: String?): Result<List<ServiceListVO>> {

        val userId = xBkAuthResourceApi.getBkUsername(bk_token)

        val startEpoch = System.currentTimeMillis()
        try {
            val serviceListVO = ArrayList<ServiceListVO>()

            val serviceTypeMap = serviceTypeDao.getAllIdAndTitle(dslContext)

            val groupService = serviceDao.getServiceList(dslContext).groupBy { it.serviceTypeId }

            val grayTest = grayTestDao.listByUser(dslContext, userId).map { it.server_id to it.status }.toMap()

            val favorServices = favoriteDao.list(dslContext, userId).map { it.serviceId }.toList()

            serviceTypeMap.forEach { serviceType ->
                val typeId = serviceType.id
                val typeName = serviceType.title
                val services = ArrayList<ServiceVO>()

                val s = groupService[typeId]

                s?.forEach {
                    val status = grayTest[it.id] ?: it.status
                    val favor = favorServices.contains(it.id)
                    services.add(
                        ServiceVO(
                            it.id,
                            it.name ?: "",
                            it.link ?: "",
                            it.linkNew ?: "",
                            status,
                            it.injectType ?: "",
                            it.iframeUrl ?: "",
                            getCSSUrl(it, projectId),
                            getJSUrl(it, projectId),
                            it.showProjectList ?: false,
                            it.showNav ?: false,
                            it.projectIdType ?: "",
                            favor,
                            it.weight ?: 0
                        )
                    )
                }

                serviceListVO.add(ServiceListVO(typeName, serviceType.weight ?: 0, services.sortedByDescending { it.weigHt }))
            }

            return Result(0, "OK", serviceListVO.sortedByDescending { it.weigHt })
        } finally {
            logger.info("It took ${System.currentTimeMillis() - startEpoch}ms to list services")
        }
    }

    // 获取CSS URL，包括灰度的
    private fun getCSSUrl(record: TServiceRecord, projectId: String?): String {
        return if (gray.isGray() && !projectId.isNullOrBlank()) {
            if (redisTemplate.opsForSet().isMember(gray.getGrayRedisKey(), projectId!!)) {
                record.grayCssUrl ?: record.cssUrl
            } else {
                record.cssUrl
            }
        } else {
            record.cssUrl
        } ?: ""
    }

    // 获取 JS URL， 包括灰度的
    private fun getJSUrl(record: TServiceRecord, projectId: String?): String {
        return if (gray.isGray() && !projectId.isNullOrBlank()) {
            if (redisTemplate.opsForSet().isMember(gray.getGrayRedisKey(), projectId)) {
                record.grayJsUrl ?: record.jsUrl
            } else {
                record.jsUrl
            }
        } else {
            record.jsUrl
        } ?: ""
    }

    companion object {
        private val logger = LoggerFactory.getLogger(UserProjectSrvService::class.java)
    }
}