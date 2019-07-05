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

package com.tencent.devops.project.service.tof

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import com.tencent.devops.common.api.exception.OperationException
import com.tencent.devops.common.api.util.HttpUtil
import com.tencent.devops.project.pojo.OrganizationInfo
import com.tencent.devops.project.pojo.enums.OrganizationType
import com.tencent.devops.project.pojo.tof.ChildDeptRequest
import com.tencent.devops.project.pojo.tof.ChildDeptResponse
import com.tencent.devops.project.pojo.tof.DeptInfo
import com.tencent.devops.project.pojo.tof.DeptInfoRequest
import com.tencent.devops.project.pojo.tof.Response
import com.tencent.devops.project.pojo.tof.StaffInfoRequest
import com.tencent.devops.project.pojo.tof.StaffInfoResponse
import com.tencent.devops.project.pojo.user.UserDeptDetail
import okhttp3.MediaType
import okhttp3.Request
import okhttp3.RequestBody
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Service


@Service
class TOFService @Autowired constructor(private val objectMapper: ObjectMapper) {

    @Value("\${tof.host:#{null}}")
    private val tofHost: String? = null

    @Value("\${tof.appCode:#{null}}")
    private val tofAppCode: String? = null

    @Value("\${tof.appSecret:#{null}}")
    private val tofAppSecret: String? = null

    fun getUserDeptDetail(bk_token: String): UserDeptDetail {
        return UserDeptDetail("", 0, "", 0, "", 0, 0, "")
    }

    fun getUserDeptDetail(userId: String, bk_ticket: String): UserDeptDetail {
        return getUserDeptDetail(null, userId, bk_ticket)
    }

    fun getOrganizationInfo(
        userId: String,
        type: OrganizationType,
        id: Int
    ): List<OrganizationInfo> {
        validate()
        return getChildDeptInfos(userId, type, id).map {
            OrganizationInfo(it.ID, it.Name)
        }
    }

    private fun getChildDeptInfos(userId: String, type: OrganizationType, id: Int): List<ChildDeptResponse> {
        try {
            logger.info("Start to get the child dept info by user $userId")
            val path = "get_child_dept_infos"
            val responseContent = request(
                path, ChildDeptRequest(
                    tofAppCode!!,
                    tofAppSecret!!,
                    getParentDeptIdByOrganizationType(type, id),
                    1
                ), "获取子部门信息失败"
            )
            val response: Response<List<ChildDeptResponse>> =
                objectMapper.readValue(responseContent)
            if (response.data == null) {
                logger.warn("Fail o get the child dept info of type $type and id $id with response $responseContent")
                throw OperationException("获取子部门信息失败")
            }
            return response.data
        } catch (t: Throwable) {
            logger.warn("Fail to get the organization info of type $type and id $id", t)
            throw OperationException("获取子部门信息失败")
        }
    }

    private fun getParentDeptIdByOrganizationType(type: OrganizationType, id: Int): Int {
        return when (type) {
            OrganizationType.bg -> 0
            else -> id
        }
    }

    private fun getStaffInfo(operator: String?, userId: String, bk_ticket: String): StaffInfoResponse {
        try {
            val path = "get_staff_info"
            val responseContent = request(
                path, StaffInfoRequest(
                    tofAppCode!!,
                    tofAppSecret!!, operator, userId, bk_ticket
                ), "获取用户信息失败"
            )
            val response: Response<StaffInfoResponse> = objectMapper.readValue(responseContent)
            if (response.data == null) {
                logger.warn("Fail to get the staff info of user $userId with bk_ticket $bk_ticket and response $responseContent")
                throw OperationException("获取用户信息失败")
            }
            return response.data
        } catch (t: Throwable) {
            logger.warn("Fail to get the staff info of userId $userId with ticket $bk_ticket", t)
            throw OperationException("获取用户信息失败")
        }
    }

    private fun getParentDeptInfo(groupId: String, level: Int): List<DeptInfo> {
        try {
            val path = "get_parent_dept_infos"
            val responseContent = request(
                path,
                DeptInfoRequest(tofAppCode!!, tofAppSecret!!, groupId, level), "获取公司组织架构信息失败"
            )
            val response: Response<List<DeptInfo>> = objectMapper.readValue(responseContent)
            if (response.data == null) {
                logger.warn("Fail to get the parent dept info of group $groupId and level $level with response $responseContent")
                throw OperationException("获取公司组织架构信息失败")
            }
            return response.data
        } catch (t: Throwable) {
            logger.warn("Fail to get the parent dept info of group $groupId and level $level", t)
            throw OperationException("获取父部门信息失败")
        }
    }

    private fun request(path: String, body: Any, errorMessage: String): String {
        val url = "http://$tofHost/component/compapi/tof/$path"
        val requestContent = objectMapper.writeValueAsString(body)
        logger.info("Start to request $url with body $requestContent")
        val requestBody = Request.Builder()
            .url(url)
            .post(RequestBody.create(MediaType.parse("application/json; charset=utf-8"), requestContent))
            .build()
        val response = request(requestBody, errorMessage)
        logger.info("Get the response $response of request $url")
        return response
    }

    private fun request(request: Request, errorMessage: String): String {
        val httpClient = HttpUtil.getHttpClient()
        httpClient.newCall(request).execute().use { response ->
            val responseContent = response.body()!!.string()
            if (!response.isSuccessful) {
                logger.warn("Fail to request $request with code ${response.code()}, message ${response.message()} and body $responseContent")
                throw RuntimeException(errorMessage)
            }
            return responseContent
        }
    }

    private fun validate() {
        if (tofHost.isNullOrBlank()) {
            throw RuntimeException("TOF HOST is empty")
        }
        if (tofAppCode.isNullOrBlank()) {
            throw RuntimeException("TOF app code is empty")
        }
        if (tofAppSecret.isNullOrBlank()) {
            throw RuntimeException("TOF app secret is empty")
        }
    }

    private fun getUserDeptDetail(operator: String?, userId: String, bk_ticket: String): UserDeptDetail {
        validate()
        val staffInfo = getStaffInfo(operator, userId, bk_ticket)
        // 通过用户组查询父部门信息　(由于tof系统接口查询结构是从当前机构往上推查询，如果创建者机构层级大于4就查不完整1到3级的机构，所以查询级数设置为10)
        val deptInfos = getParentDeptInfo(staffInfo.GroupId, 10) // 一共三级，从事业群->部门->中心
        var bgName = ""
        var bgId = 0
        var deptName = ""
        var deptId = 0
        var centerName = ""
        var centerId = 0
        val groupId = staffInfo.GroupId.toInt()
        val groupName = staffInfo.GroupName
        for (deptInfo in deptInfos) {
            val level = deptInfo.Level
            val name = deptInfo.Name
            when (level) {
                "1" -> {
                    bgName = name
                    bgId = deptInfo.ID.toInt()
                }
                "2" -> {
                    deptName = name
                    deptId = deptInfo.ID.toInt()
                }
                "3" -> {
                    centerName = name
                    centerId = deptInfo.ID.toInt()
                }
            }
        }
        return UserDeptDetail(
                bgName,
                bgId,
                deptName,
                deptId,
                centerName,
                centerId,
                groupId,
                groupName
        )
    }

    companion object {
        private val logger = LoggerFactory.getLogger(TOFService::class.java)
    }
}