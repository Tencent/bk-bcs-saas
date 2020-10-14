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

package com.tencent.devops.project.dao

import com.tencent.devops.model.project.tables.TProject
import com.tencent.devops.model.project.tables.records.TProjectRecord
import com.tencent.devops.project.pojo.*
import com.tencent.devops.project.pojo.enum.ApproveStatus
import com.tencent.devops.project.pojo.user.UserDeptDetail
import org.jooq.DSLContext
import org.jooq.Result
import org.springframework.stereotype.Repository
import java.time.LocalDateTime

@Repository
class ProjectDao {

    fun existByEnglishName(
        dslContext: DSLContext,
        englishName: String,
        projectId: String?
    ): Boolean {
        with(TProject.T_PROJECT) {
            val step = dslContext.selectFrom(this)
                .where(ENGLISH_NAME.eq(englishName))

            if (!projectId.isNullOrBlank()) {
                step.and(PROJECT_ID.ne(projectId))
            }
            return step.fetchOne() != null
        }
    }

    fun existByProjectName(
        dslContext: DSLContext,
        projectName: String,
        projectId: String?
    ): Boolean {
        with(TProject.T_PROJECT) {
            val step = dslContext.selectFrom(this)
                .where(PROJECT_NAME.eq(projectName))
            if (!projectId.isNullOrBlank()) {
                step.and(PROJECT_ID.ne(projectId))
            }
            return step.fetchOne() != null
        }
    }

    fun list(dslContext: DSLContext, projectIdList: List<String>): Result<TProjectRecord> {
        with(TProject.T_PROJECT) {
            return dslContext.selectFrom(this)
                    .where(APPROVAL_STATUS.eq(2))
                    .and(PROJECT_ID.`in`(projectIdList))
                    .and(IS_OFFLINED.eq(false)).fetch()
        }
    }

    fun get(
        dslContext: DSLContext,
        projectId: String
    ): TProjectRecord? {
        with(TProject.T_PROJECT) {
            return dslContext.selectFrom(this)
                .where(PROJECT_ID.eq(projectId)).fetchOne()
        }
    }

    fun create(dslContext: DSLContext, paasProject: PaasProject): Int {
        with(TProject.T_PROJECT) {
            return dslContext.insertInto(
                this,
                APPROVAL_STATUS,
                APPROVAL_TIME,
                APPROVER,
                BG_ID,
                BG_NAME,
                CC_APP_ID,
                CENTER_ID,
                CENTER_NAME,
                CREATED_AT,
                CREATOR,
                DATA_ID,
                DEPLOY_TYPE,
                DEPT_ID,
                DEPT_NAME,
                DESCRIPTION,
                ENGLISH_NAME,
                EXTRA,
                IS_OFFLINED,
                IS_SECRECY,
                KIND,
                LOGO_ADDR,
                PROJECT_ID,
                PROJECT_NAME,
                PROJECT_TYPE,
                REMARK,
                UPDATED_AT,
                USE_BK,
                APPROVAL_STATUS
            )
                .values(
                    paasProject.approval_status,
                    paasProject.approval_time,
                    paasProject.approver,
                    paasProject.bg_id,
                    paasProject.bg_name,
                    paasProject.cc_app_id,
                    paasProject.center_id,
                    paasProject.center_name,
                    paasProject.created_at.time,
                    paasProject.creator,
                    paasProject.data_id,
                    paasProject.deploy_type,
                    paasProject.dept_id,
                    paasProject.dept_name,
                    paasProject.description,
                    paasProject.english_name,
                    paasProject.extra,
                    paasProject.is_offlined,
                    paasProject.is_secrecy,
                    paasProject.kind,
                    paasProject.logo_addr,
                    paasProject.project_id,
                    paasProject.project_name,
                    paasProject.project_type,
                    paasProject.remark,
                    paasProject.updated_at?.time,
                    paasProject.use_bk,
                    ApproveStatus.APPROVED.status
                )
                .execute()
        }
    }

    fun create(
        dslContext: DSLContext,
        userId: String,
        logoAddress: String,
        projectCreateInfo: ProjectCreateInfo,
        userDeptDetail: UserDeptDetail,
        projectId: String
    ): Int {
        with(TProject.T_PROJECT) {
            return dslContext.insertInto(
                this,
                PROJECT_NAME,
                PROJECT_ID,
                ENGLISH_NAME,
                DESCRIPTION,
                BG_ID,
                BG_NAME,
                DEPT_ID,
                DEPT_NAME,
                CENTER_ID,
                CENTER_NAME,
                IS_SECRECY,
                KIND,
                CREATOR,
                CREATED_AT,
                PROJECT_TYPE,
                APPROVAL_STATUS,
                LOGO_ADDR,
                CREATOR_BG_NAME,
                CREATOR_DEPT_NAME,
                CREATOR_CENTER_NAME
            ).values(
                projectCreateInfo.project_name,
                projectId,
                projectCreateInfo.english_name,
                projectCreateInfo.description,
                projectCreateInfo.bg_id,
                projectCreateInfo.bg_name,
                projectCreateInfo.dept_id,
                projectCreateInfo.dept_name,
                projectCreateInfo.center_id,
                projectCreateInfo.center_name,
                projectCreateInfo.is_secrecy,
                projectCreateInfo.kind,
                userId,
                LocalDateTime.now(),
                projectCreateInfo.project_type,
                ApproveStatus.APPROVED.status,
                logoAddress,
                userDeptDetail.bg_name,
                userDeptDetail.dept_name,
                userDeptDetail.center_name
            ).execute()
        }
    }

    fun update(dslContext: DSLContext, userId: String, projectId: String, projectUpdateInfo: ProjectUpdateInfo): Int {
        with(TProject.T_PROJECT) {
            return dslContext.update(this)
                .set(PROJECT_NAME, projectUpdateInfo.project_name)
                .set(BG_ID, projectUpdateInfo.bg_id)
                .set(BG_NAME, projectUpdateInfo.bg_name)
                .set(CENTER_ID, projectUpdateInfo.center_id)
                .set(CENTER_NAME, projectUpdateInfo.center_name)
                .set(DEPT_ID, projectUpdateInfo.dept_id)
                .set(DEPT_NAME, projectUpdateInfo.dept_name)
                .set(DESCRIPTION, projectUpdateInfo.description)
                .set(ENGLISH_NAME, projectUpdateInfo.english_name)
                .set(UPDATED_AT, LocalDateTime.now())
                .set(UPDATOR, userId)
                .where(PROJECT_ID.eq(projectId)).execute()
        }
    }

    fun updateLogoAddress(dslContext: DSLContext, userId: String, projectId: String, logoAddress: String): Int {
        with(TProject.T_PROJECT) {
            return dslContext.update(this)
                .set(this.LOGO_ADDR, logoAddress)
                .set(UPDATED_AT, LocalDateTime.now())
                .set(UPDATOR, userId)
                .where(PROJECT_ID.eq(projectId)).execute()
        }
    }


    fun getProjectById(dslContext: DSLContext, projectId: String): TProjectRecord? {
        with(TProject.T_PROJECT) {
            return dslContext.selectFrom(this).where(PROJECT_ID.eq(projectId)).fetchOne()
        }
    }

    fun getProjectByCode(dslContext: DSLContext, projectCode: String): TProjectRecord? {
        with(TProject.T_PROJECT) {
            return dslContext.selectFrom(this).where(ENGLISH_NAME.eq(projectCode)).fetchOne()
        }
    }

    fun getAllProjectList(dslContext: DSLContext): Result<TProjectRecord> {
        with(TProject.T_PROJECT) {
            return dslContext.selectFrom(this).orderBy(CREATED_AT.desc()).fetch()
        }
    }

    fun updateEnabled(dslContext: DSLContext, userId: String, projectId: String, enabled: Boolean) {
        with(TProject.T_PROJECT) {
            dslContext.update(this)
                    .set(UPDATED_AT, LocalDateTime.now())
                    .set(UPDATOR, userId)
                    .set(ENABLED, enabled)
                    .where(PROJECT_ID.eq(projectId)).execute()
        }
    }

    fun listByEnglishName(dslContext: DSLContext, englishNameList: List<String>): Result<TProjectRecord> {
            with(TProject.T_PROJECT) {
                return dslContext.selectFrom(this)
                        .where(APPROVAL_STATUS.eq(2))
                        .and(ENGLISH_NAME.`in`(englishNameList))
                        .and(IS_OFFLINED.eq(false))
                        .orderBy(CREATED_AT.desc())
                        .fetch()
            }
    }

    fun listAll(dslContext: DSLContext): Result<TProjectRecord> {
        with(TProject.T_PROJECT) {
            return dslContext.selectFrom(this)
                    .where(APPROVAL_STATUS.eq(2))
                    .and(IS_OFFLINED.eq(false))
                    .orderBy(CREATED_AT.desc())
                    .fetch()
        }
    }
}