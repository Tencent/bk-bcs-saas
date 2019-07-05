/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

// 0: 置灰, 1: 可用, -1: 隐藏
const OPERATE_MAP = {
    // 扩缩容操作
    'scale': -1,
    // 滚动升级操作
    'rollingupdate': -1,
    // 暂停滚动升级操作
    'pause': -1,
    // 恢复滚动升级操作
    'resume': -1,
    // 取消滚动升级操作
    'cancel': -1,

    // mesos 的 application 的更新操作，
    // 和 mesos 的 deployment 的滚动升级的状态限制一样
    'update': -1,
    // 重建操作
    'rebuild': -1,
    // 删除操作
    'delete': -1,
    // 只有当 backend_status 为 BackendError 时才出现，显示的操作为重试和删除
    'again': -1,
    // 是否显示名称前面的 loading 效果
    // category 为 application 时，
    // 只有 application_status 为 Deploying 和 Operating 为才显示
    'showLoading': false,
    // 是否显示 感叹号 error 提示
    'showError': false
}

export default class State {
    constructor (props) {
        this.category = props.category
        this.backendStatus = props.backendStatus
        this.applicationStatus = props.applicationStatus
        this.deploymentStatus = props.deploymentStatus
        // 这个属性表示是否锁住当前状态对应的操作，目的是在发送请求时，锁住操作
        this.islock = props.islock
    }

    transition (backendStatus, applicationStatus, deploymentStatus) {
        this.backendStatus = backendStatus
        this.applicationStatus = applicationStatus
        this.deploymentStatus = deploymentStatus
        return this.getRet()
    }

    getRet () {
        if (this.backendStatus === 'BackendError') {
            return Object.assign({}, OPERATE_MAP, {
                // 重试
                'again': 1,
                'delete': 1
            })
        }
        const invoke = this.category === 'application' ? 'getAppRet' : 'getDeployRet'
        return this[invoke]()
    }

    getAppRet () {
        let ret = {}
        switch (this.applicationStatus) {
            // 扩缩容 置灰，删除 重建 可用
            case 'Staging':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 扩缩容
                    'scale': 0,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1,
                    'showError': true
                })
                break
            // 扩缩容 置灰，删除 重建 可用
            case 'Deploying':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 扩缩容
                    'scale': 0,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1,
                    // 是否显示 loading
                    'showLoading': true
                })
                break
            // 扩缩容 删除 重建 可用
            case 'Running':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 更新
                    'update': 1,
                    // 扩缩容
                    'scale': 1,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1
                })
                break
            // 扩缩容 置灰，删除 重建 可用
            case 'Finish':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 扩缩容
                    'scale': 0,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1
                })
                break
            // 扩缩容 置灰，删除 重建 可用
            case 'Error':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 扩缩容
                    'scale': 0,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1,
                    'showError': true
                })
                break
            // 扩缩容 置灰，删除 重建 可用
            case 'Operating':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 扩缩容
                    'scale': 0,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1,
                    // 是否显示 loading
                    'showLoading': true
                })
                break
            // 扩缩容 删除 重建 可用
            case 'Unnormal':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 扩缩容
                    'scale': 1,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1,
                    'showError': true
                })
                break
            case 'Abnormal':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 更新
                    'update': 1,
                    // 扩缩容
                    'scale': 1,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1,
                    'showError': true
                })
                break
            // 给一个都没匹配到的状态，扩缩容 删除 重建 可用，避免出现操作按钮不出现的情况
            default:
                ret = Object.assign({}, OPERATE_MAP, {
                    // 扩缩容
                    'scale': 1,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1
                })
        }

        return ret
    }

    getDeployRet () {
        let ret = {}
        switch (this.deploymentStatus) {
            // deployment_status 为 Deploying 时，
            // application_status 的 Staging Error RollingUpdate Unnormal 状态不可能存在
            case 'Deploying':
                // 滚动升级 扩缩容 置灰，删除 重建 可用
                if (this.applicationStatus === 'Deploying' || this.applicationStatus === 'Operating') {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级
                        'rollingupdate': 0,
                        // 扩缩容
                        'scale': 0,
                        // 重建
                        'rebuild': 1,
                        // 删除
                        'delete': 1,
                        'showLoading': true
                    })
                } else if (this.applicationStatus === 'Running' || this.applicationStatus === 'Finish') {
                    // 滚动升级 扩缩容 删除 重建 可用
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级
                        'rollingupdate': 1,
                        // 扩缩容
                        'scale': 1,
                        // 重建
                        'rebuild': 1,
                        // 删除
                        'delete': 1,
                        'showLoading': true
                    })
                }
                break

            case 'Running':
                // 滚动升级 扩缩容 置灰，删除 重建 可用
                if (this.applicationStatus === 'Staging' || this.applicationStatus === 'Deploying'
                        || this.applicationStatus === 'Finish' || this.applicationStatus === 'Error'
                        || this.applicationStatus === 'Operating'
                ) {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级
                        'rollingupdate': 0,
                        // 扩缩容
                        'scale': 0,
                        // 重建
                        'rebuild': 1,
                        // 删除
                        'delete': 1,
                        'showError': this.applicationStatus === 'Staging' || this.applicationStatus === 'Error',
                        'showLoading': this.applicationStatus === 'Deploying'
                    })
                } else if (this.applicationStatus === 'Running' || this.applicationStatus === 'Unnormal' || this.applicationStatus === 'Abnormal') {
                    // 滚动升级 扩缩容 删除 重建 可用
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级
                        'rollingupdate': 1,
                        // 扩缩容
                        'scale': 1,
                        // 重建
                        'rebuild': 1,
                        // 删除
                        'delete': 1,
                        'showError': this.applicationStatus === 'Unnormal' || this.applicationStatus === 'Abnormal'
                    })
                } else if (this.applicationStatus === 'RollingUpdate') {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级
                        'rollingupdate': 0,
                        // 扩缩容
                        'scale': 0,
                        // 重建
                        'rebuild': 1,
                        // 删除
                        'delete': 1,
                        'showLoading': true
                    })
                }
                break

            // 无论 application_status 是什么状态，都不允许任何操作
            case 'Deleting':
                ret = Object.assign({}, OPERATE_MAP, {
                    // 滚动升级
                    'rollingupdate': 0,
                    // 扩缩容
                    'scale': 0,
                    // 重建
                    'rebuild': 0,
                    // 删除
                    'delete': 0,
                    'showLoading': true
                })
                break

            // application_status 只能是 RollingUpdate
            case 'Update':
                // 暂停滚动升级、取消滚动升级可用，重建，删除可用
                if (this.applicationStatus === 'RollingUpdate') {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 暂停滚动升级
                        'pause': 1,
                        // 取消滚动升级
                        'cancel': 1,
                        // 重建
                        'rebuild': 1,
                        // 删除
                        'delete': 1,
                        'showLoading': true
                    })
                } else {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级
                        'rollingupdate': 0,
                        // 扩缩容
                        'scale': 0,
                        // 重建
                        'rebuild': 0,
                        // 删除
                        'delete': 0,
                        'showLoading': true
                    })
                }
                break

            // application_status 只能是 RollingUpdate
            case 'UpdatePaused':
                // 恢复滚动升级、取消滚动升级可用，重建，删除可用
                if (this.applicationStatus === 'RollingUpdate') {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 恢复滚动升级
                        'resume': 1,
                        // 取消滚动升级
                        'cancel': 1,
                        // 重建
                        'rebuild': 1,
                        // 删除
                        'delete': 1
                    })
                } else {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级
                        'rollingupdate': 0,
                        // 扩缩容
                        'scale': 0,
                        // 重建
                        'rebuild': 0,
                        // 删除
                        'delete': 0
                    })
                }
                break

            // application_status 只能是 RollingUpdate
            case 'UpdateSuspend':
                // 恢复滚动升级、取消滚动升级可用，重建，删除可用
                if (this.applicationStatus === 'RollingUpdate') {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 恢复滚动升级
                        'resume': 1,
                        // 取消滚动升级
                        'cancel': 0,
                        // 重建
                        'rebuild': 1,
                        // 删除
                        'delete': 1
                    })
                } else {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级
                        'rollingupdate': 0,
                        // 扩缩容
                        'scale': 0,
                        // 重建
                        'rebuild': 0,
                        // 删除
                        'delete': 0
                    })
                }
                break
            // 给一个都没匹配到的状态，滚动升级 扩缩容 删除 重建 可用，避免出现操作按钮不出现的情况
            default:
                ret = Object.assign({}, OPERATE_MAP, {
                    // 滚动升级
                    'rollingupdate': 1,
                    // 扩缩容
                    'scale': 1,
                    // 重建
                    'rebuild': 1,
                    // 删除
                    'delete': 1
                })
        }
        return ret
    }

    lock () {
        this.islock = true
    }

    unlock () {
        this.islock = false
    }
}
