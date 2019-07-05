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
    scale: -1,
    rollingupdate: -1,
    rebuild: -1,
    delete: -1,
    pause: -1,
    resume: -1,
    cancel: -1,
    // 只有当 backend_status 为 BackendError 时才出现，显示的操作为重试和删除
    again: -1,
    // 是否显示名称前面的 loading 效果
    // category 为 application 时，只有 application_status 为 Deploying 和 Operating 为才显示
    showLoading: false,
    // 是否显示 感叹号 error 提示
    showError: false
}

export default class State {
    constructor (props) {
        this.status = props.status
        this.backendStatus = props.backendStatus
        this.instance = props.instance
        this.buildInstance = props.buildInstance
        this.operType = props.operType
        // backend_error && oper_type==create，oper_type_flag 为空
        // 否则，oper_type_flag 和 oper_type 同一个值，表示前端不显示重试+删除；显示的是这个值对应的操作，并且加上 error 的感叹号
        this.operTypeFlag = props.operTypeFlag
        // 这个属性表示是否锁住当前状态对应的操作，目的是在发送请求时，锁住操作
        this.islock = props.islock
    }

    lock () {
        this.islock = true
    }

    unlock () {
        this.islock = false
    }

    getRet () {
        let ret = {}

        // backend_error && oper_type==create，oper_type_flag 为空
        // 否则，oper_type_flag 和 oper_type 同一个值，表示前端不显示重试+删除；显示的是这个值对应的操作，并且加上 error 的感叹号
        if (this.operTypeFlag) {
            return this._checkStatus(this.operTypeFlag)
        }

        // 如果 operType === create ，才是 again，delete 操作
        if (this.backendStatus === 'BackendError' && this.operType === 'create') {
            ret = Object.assign({}, OPERATE_MAP, {
                // 重试
                again: 1,
                // 删除
                delete: 1,
                showError: true
            })
            return ret
        }

        ret = this._checkStatus(this.operType)
        return ret
    }

    _checkStatus (operType) {
        let ret = {}
        switch (this.status) {
            case 'Unready':
                // 允许删除和重建
                if (this.instance === 0) {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级置灰
                        rollingupdate: 0,
                        // 扩缩容置灰
                        scale: 0,
                        // 重建可用
                        rebuild: 1,
                        // 删除可用
                        delete: 1,
                        showLoading: true
                    })
                } else {
                    // 允许暂停、撤销、删除、重建
                    if (operType === 'resume' || operType === 'rollingupdate' || operType === 'cancel') {
                        if (this.buildInstance !== this.instance) {
                            ret = Object.assign({}, OPERATE_MAP, {
                                // 暂停可用
                                pause: 1,
                                // 撤销可用
                                cancel: 1,
                                // 重建可用
                                rebuild: 1,
                                // 删除可用
                                delete: 1,
                                showError: false,
                                showLoading: true
                            })
                        } else {
                            ret = Object.assign({}, OPERATE_MAP, {
                                // 暂停可用
                                pause: 1,
                                // 撤销可用
                                cancel: 1,
                                // 重建可用
                                rebuild: 1,
                                // 删除可用
                                delete: 1,
                                showLoading: true
                            })
                        }
                    } else if (operType === 'create' || operType === 'scale' || operType === 'rebuild') {
                        // 允许删除、重建
                        ret = Object.assign({}, OPERATE_MAP, {
                            // 滚动升级
                            rollingupdate: 1,
                            // 扩缩容
                            scale: 1,
                            // 重建可用
                            rebuild: 1,
                            // 删除可用
                            delete: 1,
                            showLoading: true
                        })
                    } else {
                        // delete, 所有操作都不允许
                        ret = Object.assign({}, OPERATE_MAP, {
                            // 滚动升级置灰
                            rollingupdate: 0,
                            // 扩缩容置灰
                            scale: 0,
                            // 重建置灰
                            rebuild: 0,
                            // 删除置灰
                            delete: 0,
                            showLoading: true
                        })
                    }
                }
                break
            case 'Running':
                // 允许删除和重建，Running 时 instance 不可能是 0
                if (this.instance === 0) {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级置灰
                        rollingupdate: 0,
                        // 扩缩容置灰
                        scale: 0,
                        // 重建可用
                        rebuild: 1,
                        // 删除可用
                        delete: 1
                    })
                } else {
                    // 允许滚动升级、扩缩容、删除、重建
                    if (operType === 'create' || operType === 'rollingupdate'
                        || operType === 'scale' || operType === 'rebuild' || operType === 'cancel'
                    ) {
                        ret = Object.assign({}, OPERATE_MAP, {
                            // 滚动升级可以
                            rollingupdate: 1,
                            // 扩缩容可以
                            scale: 1,
                            // 重建可用
                            rebuild: 1,
                            // 删除可用
                            delete: 1
                        })
                    } else if (operType === 'resume') {
                        // 允许暂停、撤销、删除、重建
                        if (this.buildInstance !== this.instance) {
                            ret = Object.assign({}, OPERATE_MAP, {
                                // 暂停可用
                                pause: 1,
                                // 撤销可用
                                cancel: 1,
                                // 重建可用
                                rebuild: 1,
                                // 删除可用
                                delete: 1,
                                showError: false,
                                showLoading: true
                            })
                        } else {
                            ret = Object.assign({}, OPERATE_MAP, {
                                // 滚动升级可以
                                rollingupdate: 1,
                                // 扩缩容可以
                                scale: 1,
                                // 重建可用
                                rebuild: 1,
                                // 删除可用
                                delete: 1
                            })
                        }
                    } else {
                        // delete, 所有操作都不允许
                        ret = Object.assign({}, OPERATE_MAP, {
                            // 滚动升级置灰
                            rollingupdate: 0,
                            // 扩缩容置灰
                            scale: 0,
                            // 重建置灰
                            rebuild: 0,
                            // 删除置灰
                            delete: 0,
                            showLoading: true
                        })
                    }
                }
                break
            case 'Paused':
                // 允许恢复、删除、重建
                if (operType === 'rollingupdate' || operType === 'pause') {
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 恢复可用
                        resume: 1,
                        // 重建可用
                        rebuild: 1,
                        // 删除可用
                        delete: 1
                    })
                } else {
                    // delete, 所有操作都不允许
                    ret = Object.assign({}, OPERATE_MAP, {
                        // 滚动升级置灰
                        rollingupdate: 0,
                        // 扩缩容置灰
                        scale: 0,
                        // 重建置灰
                        rebuild: 0,
                        // 删除置灰
                        delete: 0,
                        showLoading: true
                    })
                }
                break
        }
        return ret
    }
}
