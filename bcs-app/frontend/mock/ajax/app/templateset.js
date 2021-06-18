/**
 * @file cluster all
 */

import moment from 'moment'
import faker from 'faker'

import {randomInt, sleep} from '../util'

export async function response (getArgs, postArgs, req) {
    console.log('req', req.method)
    console.log('getArgs', getArgs)
    console.log('postArgs', postArgs)
    const invoke = getArgs.invoke
    if (invoke === 'createBcsTls') {
        const ret = {
            "code": 0,
            "message": "Created",
            "data": {
                "id": 2,
                "name": "test1",
                "cert": "1111111111111111",
                "key": "22222222222",
                "creator": "admin",
                "created": "2019-01-31 11:42:55",
                "updated": "2019-01-31 11:42:55",
                "updator": ""
            }
        }
        return ret
    }
    else if (invoke === 'getCertList') {
        const ret = {
            "status": 0,
            "data": {
                "count": 2,
                "page": 0,
                "pageSize": 10000,
                "totalPages": 1,
                "records": [
                    {
                        "certId": "perrier.ffm",          // select 下拉框中 value 和 text 都为 certId 的值
                        "certType": "bcstls",             // certType 也保存到json中，传给后台，用来区分是容器服务自身的证书 还是 蓝盾的证书
                        "creator": "jiayuan",
                        "certRemark": "",
                        "createTime": 1534215869,
                        "expireTime": 1849835069,
                        "credentialId": ""
                    },
                    {
                        "certId": "jiayuan.test",
                        "certType": "tls",
                        "creator": "jiayuan",
                        "certRemark": "这是一个测试正式",
                        "createTime": 1534215516,
                        "expireTime": 1849834716,
                        "credentialId": ""
                    }
                ]
            },
            "code": 0
        }

        return ret
    }

    else if (invoke === 'getTlsDetail') {
        const ret = {
            "code": 0,
            "message": "OK",
            "data": {
                "id": 1,
                "name": "jiayuantest",
                "cert": "1111111111111111",
                "key": "22222222222",
                "creator": "admin",
                "created": "2019-01-31 11:41:14",
                "updated": "2019-01-31 11:41:14",
                "updator": ""
            }
        }

        return ret
    }

    else if (invoke === 'updateBcsTls') {
        const ret = {
            "code": 0,
            "message": "OK",
            "data": {
                "id": 1,
                "name": "jiayuantest",
                "cert": "1111111111111111",
                "key": "333333",
                "creator": "admin",
                "created": "2019-01-31 11:41:14",
                "updated": "2019-01-31 11:43:43",
                "updator": "admin"
            }
        }

        return ret
    }

    else if (invoke === 'deleteBcsTls') {
        const ret = {
            "code": 0,
            "message": "OK",
            "data": {
                "id": "1"
            }
        }

        return ret
    }

    return {
        code: 0,
        data: {}
    }
}

