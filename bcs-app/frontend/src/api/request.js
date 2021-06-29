import http from '@open/api'
import { json2Query } from '@open/common/util'
import router from '@open/router'
import store from '@open/store'

const methodsWithoutData = ['delete', 'get', 'head', 'options']
const defaultConfig = {}

export const request = (method, url) => (params = {}, config = {}) => {
    const reqMethod = method.toLowerCase()
    const reqConfig = Object.assign(defaultConfig, config)

    // 全局URL变量替换
    const variableData = {
        '$projectId': router.currentRoute.params.projectId,
        '$clusterId': store.state.curClusterId || ''
        // '$namespace': ''
    }
    Object.keys(params).forEach(key => {
        // 自定义url变量
        if (key.indexOf('$') === 0) {
            variableData[key] = params[key]
        }
    })
    let newUrl = `${DEVOPS_BCS_API_URL}${url}`
    Object.keys(variableData).forEach(key => {
        if (!variableData[key]) {
            console.warn(`路由变量未配置${key}`)
        }
        newUrl = newUrl.replace(new RegExp(`\\${key}`, 'g'), variableData[key])
        delete params[key]
    })

    let req = null
    if (methodsWithoutData.includes(reqMethod)) {
        const query = json2Query(params, '')
        if (query) {
            newUrl += `?${query}`
        }
        req = http[reqMethod](newUrl, null, reqConfig)
    } else {
        req = http[reqMethod](newUrl, params, reqConfig)
    }
    return req.then((res) => {
        return Promise.resolve(res.data)
    }).catch((err) => {
        console.log('request error', err)
        return Promise.reject(err)
    })
}

export default request
