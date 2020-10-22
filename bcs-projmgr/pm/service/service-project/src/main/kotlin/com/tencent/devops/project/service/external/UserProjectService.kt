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

import com.tencent.devops.common.api.exception.CustomException
import com.tencent.devops.common.api.exception.OperationException
import com.tencent.devops.common.api.util.DateTimeUtil
import com.tencent.devops.common.api.util.UUIDUtil
import com.tencent.devops.model.project.tables.records.TProjectRecord
import com.tencent.devops.project.api.*
import com.tencent.devops.project.dao.ProjectDao
import com.tencent.devops.project.jmx.api.JmxApi
import com.tencent.devops.project.pojo.*
import com.tencent.devops.project.pojo.enums.ProjectValidateType
import com.tencent.devops.project.pojo.user.UserDeptDetail
import org.glassfish.jersey.media.multipart.FormDataContentDisposition
import org.jooq.DSLContext
import org.jooq.impl.DSL
import org.slf4j.LoggerFactory
import org.springframework.dao.DuplicateKeyException
import org.springframework.stereotype.Service
import java.awt.AlphaComposite
import java.awt.BasicStroke
import java.awt.Color
import java.awt.Font
import java.awt.image.BufferedImage
import java.io.File
import java.io.InputStream
import java.nio.file.Files
import java.util.*
import java.util.regex.Pattern
import javax.imageio.ImageIO
import javax.ws.rs.core.Response

@Service
class UserProjectService constructor(
        private val xBkAuthResourceApi: XBkAuthResourceApi,
        private val xBkAuthPermissionApi: XBkAuthPermissionApi,
        private val dslContext: DSLContext,
        private val projectDao: ProjectDao,
        private val jmxApi: JmxApi,
        private val externalPaasCCProjectConsumer: ExternalPaasCCProjectConsumer
) {

    companion object {
        private val logger = LoggerFactory.getLogger(UserProjectService::class.java)
        const val ENGLISH_NAME_PATTERN = "[a-z][a-zA-Z0-9]+"
    }

    fun getExternalProjectList(bkToken: String): List<ProjectVO> {
        val userId = xBkAuthResourceApi.getBkUsername(bkToken)
        val startEpoch = System.currentTimeMillis()
        var success = false
        try {

            val map = xBkAuthPermissionApi.getUserResourcesByPermissions(
                    userId = userId,
                    userType = "user",
                    scopeType = XBkAuthScopeType.SYSTEM,
                    resourceType = XBkAuthResourceType.PROJECT,
                    permissions = setOf(XBkAuthPermission.MANAGE),
                    systemCode = XBkAuthSystemCode.DEVOPS_PROJECT,
                    supplier = null
            )
            val englishNameList = mutableListOf<String>()
            map.map { englishNameList.addAll(it.value) }
//            不再从iam获取项目信息
//            val resourceIdList = xBkAuthResourceApi.getUserAuthorizedScopes(userId)
//            if (resourceIdList.bk_error_code != 0) {
//                logger.warn("Fail to get the project info with response $resourceIdList")
//                throw OperationException("从权限中心获取用户的项目信息失败")
//            }
//            if (resourceIdList.data == null) {
//                return emptyList()
//            }
//
//            val englishNameList = resourceIdList.data.map
//                it.split(":")[1]
//            }
            val list = ArrayList<ProjectVO>()
            projectDao.listByEnglishName(dslContext, englishNameList).map {
                list.add(packagingBean(it))
            }

            projectDao.listAll(dslContext).map {
                if(!englishNameList.contains(it.englishName)) {
                    list.add(packagingBean(it,false))
                }
            }

            success = true
            return list
        } catch (e: Exception) {
            logger.warn("Fail to get the project list with token - $bkToken", e)
            throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Failed to get project list.")
        } finally {
            jmxApi.execute(JmxApi.PROJECT_LIST, System.currentTimeMillis() - startEpoch, success)
            logger.info("It took ${System.currentTimeMillis() - startEpoch}ms to list projects")
        }
    }


    fun getExternalAllProjectList(bkToken: String): List<ProjectVO> {
        val startEpoch = System.currentTimeMillis()
        var success = false
        try {
            val list = ArrayList<ProjectVO>()

            projectDao.getAllProjectList(dslContext).map {
                list.add(packagingBean(it))
            }
            success = true
            return list
        } catch (e: Exception) {
            throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Failed to get project list.")
        } finally {
            jmxApi.execute(JmxApi.PROJECT_LIST, System.currentTimeMillis() - startEpoch, success)
            logger.info("It took ${System.currentTimeMillis() - startEpoch}ms to list projects")
        }
    }

    fun getExternalProject(bkToken: String, projectId: String): ProjectVO? {
        val startEpoch = System.currentTimeMillis()
        var success = false
        try {
            val projectRecord = projectDao.getProjectById(dslContext,projectId)
            val projectInfo = if(projectRecord != null) {
                packagingBean(projectRecord)
            }else {
                null
            }
            success = true
            return projectInfo
        } catch (e: Exception) {
            throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Failed to get project list.")
        } finally {
            jmxApi.execute(JmxApi.PROJECT_LIST, System.currentTimeMillis() - startEpoch, success)
            logger.info("It took ${System.currentTimeMillis() - startEpoch}ms to list projects")
        }
    }


    fun getExternalProjectByCode(bkToken: String, projectCode: String): ProjectVO? {
        val startEpoch = System.currentTimeMillis()
        var success = false
        try {
            val projectRecord = projectDao.getProjectByCode(dslContext,projectCode)
            val projectInfo = if(projectRecord != null) {
                packagingBean(projectRecord)
            }else {
                null
            }
            success = true
            return projectInfo
        } catch (e: Exception) {
            throw CustomException(Response.Status.INTERNAL_SERVER_ERROR, "Failed to get project list.")
        } finally {
            jmxApi.execute(JmxApi.PROJECT_LIST, System.currentTimeMillis() - startEpoch, success)
            logger.info("It took ${System.currentTimeMillis() - startEpoch}ms to list projects")
        }
    }

    fun create(bkToken: String, projectCreateInfo: ProjectCreateInfo): Result<Boolean> {
        validate(ProjectValidateType.project_name, projectCreateInfo.project_name)
        validate(ProjectValidateType.english_name, projectCreateInfo.english_name)

        val accessToken = xBkAuthResourceApi.getAccessToken(bkToken)
        val userId = xBkAuthResourceApi.getBkUsername(bkToken)
        val startEpoch = System.currentTimeMillis()
        var success = false
        try {
            // 随机生成图片
            val logoFile = drawImage(projectCreateInfo.english_name.substring(0, 1).toUpperCase())
            try {
                // 发送服务器
                val logoAddress = ""

                // 注册项目到权限中心
                val resourceId = projectCreateInfo.english_name
                xBkAuthResourceApi.createResource(
                        XBkAuthSystemCode.DEVOPS_PROJECT,
                        "user", userId,
                        XBkAuthScopeType.SYSTEM,
                        XBkAuthSystemCode.DEVOPS_PROJECT.value,
                        XBkAuthResourceType.PROJECT,
                        resourceId,
                        projectCreateInfo.project_name
                )

                val projectId = UUIDUtil.generate()
                //   val userDeptDetail = tofService.getUserDeptDetail(userId, "") // 获取用户机构信息
                val userDeptDetail = UserDeptDetail(projectCreateInfo.bg_name, projectCreateInfo.bg_id.toInt(),
                        projectCreateInfo.dept_name, projectCreateInfo.dept_id.toInt(), projectCreateInfo.center_name,
                        projectCreateInfo.center_id.toInt(), 0, "")
                try {
                    dslContext.transaction { configuration ->
                        projectDao.create(DSL.using(configuration), userId, logoAddress, projectCreateInfo, userDeptDetail, projectId)
                        externalPaasCCProjectConsumer.onRecvProjectCreateMessage(
                                PaasCCCreateProject(
                                        userId,
                                        accessToken,
                                        projectId,
                                        0,
                                        projectCreateInfo
                                )
                        )
                    }
                } catch (e: DuplicateKeyException) {
                    logger.warn("Duplicate project $projectCreateInfo", e)
                    throw OperationException("Project Name or Project Code is dumplicate.")
                } catch (t: Throwable) {
                    logger.warn("Fail to create the project ($projectCreateInfo)", t)
                    xBkAuthResourceApi.deleteResource(XBkAuthSystemCode.DEVOPS_PROJECT, XBkAuthScopeType.SYSTEM,
                            XBkAuthSystemCode.DEVOPS_PROJECT.value, XBkAuthResourceType.PROJECT, resourceId)
                    throw t
                }


                success = true
            } finally {
                if (logoFile.exists()) {
                    logoFile.delete()
                }
            }
        } finally {
            jmxApi.execute(JmxApi.PROJECT_CREATE, System.currentTimeMillis() - startEpoch, success)
        }
        return Result(success)
    }

    fun update(
            bkToken: String,
            projectId: String,
            projectUpdateInfo: ProjectUpdateInfo
    ): Result<Boolean> {
        val accessToken = xBkAuthResourceApi.getAccessToken(bkToken)
        val userId = xBkAuthResourceApi.getBkUsername(bkToken)

        val startEpoch = System.currentTimeMillis()
        var success = false
        val tProjectRecord = projectDao.get(dslContext, projectId)
        if (tProjectRecord != null && tProjectRecord.englishName != null) {
            val resourceId = projectUpdateInfo.english_name
            try {
                try {
                    dslContext.transaction { configuration ->
                        xBkAuthResourceApi.modifyResource(
                                XBkAuthSystemCode.DEVOPS_PROJECT,
                                XBkAuthScopeType.SYSTEM, XBkAuthSystemCode.DEVOPS_PROJECT.value,
                                XBkAuthResourceType.PROJECT, resourceId, projectUpdateInfo.project_name
                        )
                        projectDao.update(DSL.using(configuration), userId, projectId, projectUpdateInfo)
                        externalPaasCCProjectConsumer.onRecvProjectUpdateMessage(
                                PaasCCUpdateProject(
                                        userId,
                                        accessToken,
                                        projectId,
                                        0,
                                        projectUpdateInfo
                                )
                        )
                    }
                } catch (e: DuplicateKeyException) {
                    logger.warn("Duplicate project $projectUpdateInfo", e)
                    xBkAuthResourceApi.modifyResource(XBkAuthSystemCode.DEVOPS_PROJECT,
                            XBkAuthScopeType.SYSTEM, XBkAuthSystemCode.DEVOPS_PROJECT.value,
                            XBkAuthResourceType.PROJECT, resourceId, projectUpdateInfo.project_name)
                    throw OperationException("Project Name or Project Code is dumplicate.")
                }


                success = true
            } finally {
                jmxApi.execute(JmxApi.PROJECT_UPDATE, System.currentTimeMillis() - startEpoch, success)
            }
        } else {
            logger.warn("ProjectID is invalid")
            throw OperationException("Project Id is invalid.")
        }
        return Result(success)
    }

    fun updateLogo(
            bkToken: String,
            projectId: String,
            inputStream: InputStream,
            disposition: FormDataContentDisposition
    ): Result<Boolean> {
        logger.info("Update the logo of project $projectId")

        val accessToken = xBkAuthResourceApi.getAccessToken(bkToken)
        val userId = xBkAuthResourceApi.getBkUsername(bkToken)
        val project = projectDao.get(dslContext, projectId)
        if (project != null) {
            var logoFile: File? = null
            try {
                logoFile = convertFile(inputStream)
                val logoAddress = ""

                dslContext.transaction { configuration ->
                    projectDao.updateLogoAddress(DSL.using(configuration), userId, projectId, logoAddress)
                    externalPaasCCProjectConsumer.onRecvProjectLogoUpdateMessage(
                            PaasCCUpdateProjectLogo(
                                    userId,
                                    accessToken,
                                    projectId,
                                    0,
                                    ProjectUpdateLogoInfo(logoAddress, userId)
                            )
                    )
                }
            } catch (e: Exception) {
                logger.warn("fail update projectLogo", e)
                throw OperationException("Failed to update project logo.")
            } finally {
                logoFile?.delete()
            }
        } else {
            logger.warn("$project is null or $project is empty")
            throw OperationException("Can not found  project")
        }
        return Result(true)
    }

    fun validate(
            bkToken: String,
            validateType: ProjectValidateType,
            name: String,
            project_id: String?
    ): Result<Boolean> {
        validate(validateType, name, project_id)
        return Result(true)
    }

    private fun validate(
            validateType: ProjectValidateType,
            name: String,
            projectId: String? = null
    ) {
        if (name.isBlank()) {
            throw OperationException("Project Name can not be null.")
        }
        when (validateType) {
            ProjectValidateType.project_name -> {
                if (name.length < 4) {
                    throw OperationException("Project Name must more than 4 characters.")
                }
                if (name.length > 12) {
                    throw OperationException("Project Name must less than 12 characters.")
                }
                if (projectDao.existByProjectName(dslContext, name, projectId)) {
                    throw OperationException("Project name is existed")
                }
            }
            ProjectValidateType.english_name -> {
                // 2 ~ 32 个字符+数字，以小写字母开头
                if (name.length < 2) {
                    throw OperationException("Project Code must more than 2 characters.")
                }
                if (name.length > 32) {
                    throw OperationException("Project Code must less than 32 characters.")
                }
                if (!Pattern.matches(ENGLISH_NAME_PATTERN, name)) {
                    logger.warn("Project English Name($name) is not match")
                    throw OperationException("English name is composed of characters + numbers and starts with lowercase letters.")
                }
                if (projectDao.existByEnglishName(dslContext, name, projectId)) {
                    throw OperationException("Project Code already exists.")
                }
            }
        }
    }

    private fun convertFile(inputStream: InputStream): File {
        val logo = Files.createTempFile("default_", ".png").toFile()

        logo.outputStream().use {
            inputStream.copyTo(it)
        }

        return logo
    }

    private fun packagingBean(tProjectRecord: TProjectRecord,permission: Boolean? = true): ProjectVO {
        return ProjectVO(
                tProjectRecord.id,
                tProjectRecord.projectId ?: "",
                tProjectRecord.projectName,
                tProjectRecord.englishName ?: "",
                tProjectRecord.projectType ?: 0,
                tProjectRecord.approvalStatus ?: 0,
                if (tProjectRecord.approvalTime == null) {
                    ""
                } else {
                    DateTimeUtil.toDateTime(tProjectRecord.approvalTime, "yyyy-MM-dd HH:mm:ss")
                },
                tProjectRecord.approver ?: "",
                tProjectRecord.bgId, tProjectRecord.bgName ?: "",
                tProjectRecord.ccAppId ?: 0,
                tProjectRecord.ccAppName ?: "",
                tProjectRecord.centerId ?: 0,
                tProjectRecord.centerName ?: "",
                DateTimeUtil.toDateTime(tProjectRecord.createdAt, "yyyy-MM-dd HH:mm:ss"),
                tProjectRecord.creator ?: "",
                tProjectRecord.dataId ?: 0,
                tProjectRecord.deployType ?: "",
                tProjectRecord.deptId ?: 0,
                tProjectRecord.deptName ?: "",
                tProjectRecord.description ?: "",
                tProjectRecord.englishName ?: "",
                tProjectRecord.extra ?: "",
                tProjectRecord.isOfflined,
                tProjectRecord.isSecrecy,
                tProjectRecord.isHelmChartEnabled,
                tProjectRecord.kind,
                tProjectRecord.logoAddr ?: "",
                tProjectRecord.remark ?: "",
                if (tProjectRecord.updatedAt == null) {
                    ""
                } else {
                    DateTimeUtil.toDateTime(tProjectRecord.updatedAt, "yyyy-MM-dd HH:mm:ss")
                },
                tProjectRecord.useBk,
                tProjectRecord.enabled ?: false,
                false,
                permission
        )
    }


    private fun drawImage(logoStr: String): File {
        val logoBackgroundColor = arrayOf("#FF5656", "#FFB400", "#30D878", "#3C96FF")
        val max = logoBackgroundColor.size - 1
        val min = 0
        val random = Random()
        val backgroundIndex = random.nextInt(max) % (max - min + 1) + min
        val width = 128
        val height = 128
        // 创建BufferedImage对象
        val bi = BufferedImage(width, height, BufferedImage.TYPE_INT_RGB)
        // 获取Graphics2D
        val g2d = bi.createGraphics()
        // 设置透明度
        g2d.composite = AlphaComposite.getInstance(AlphaComposite.SRC_ATOP, 1.0f)

        when (backgroundIndex) {
            0 -> {
                g2d.background = Color.RED
            }
            1 -> {
                g2d.background = Color.YELLOW
            }
            2 -> {
                g2d.background = Color.GREEN
            }
            3 -> {
                g2d.background = Color.BLUE
            }
        }
        g2d.clearRect(0, 0, width, height)
        g2d.color = Color.WHITE
        g2d.stroke = BasicStroke(1.0f)
        val font = Font("宋体", Font.PLAIN, 64)
        g2d.font = font
        val fontMetrics = g2d.fontMetrics
        val heightAscent = fontMetrics.ascent

        val context = g2d.fontRenderContext
        val stringBounds = font.getStringBounds(logoStr, context)
        val fontWidth = stringBounds.width.toFloat()

        g2d.drawString(
                logoStr,
                (width / 2 - fontWidth / 2),
                (height / 2 + heightAscent / 2).toFloat()
        )
        // 透明度设置 结束
        g2d.composite = AlphaComposite.getInstance(AlphaComposite.SRC_OVER)
        // 释放对象
        g2d.dispose()
        // 保存文件
        val logo = Files.createTempFile("default_", ".png").toFile()
        ImageIO.write(bi, "png", logo)
        return logo
    }

}