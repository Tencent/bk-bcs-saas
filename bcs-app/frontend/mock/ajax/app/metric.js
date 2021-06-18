/**
 * @file metric all
 * @author hieiwang <hieiwang@tencent.com>
 */

import moment from 'moment'
import faker from 'faker'
import chalk from 'chalk'

import {randomInt, sleep} from '../util'

export async function response(getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    console.log()
    const invoke = getArgs.invoke
    if (invoke === 'getMetricList') {
        const COUNT = randomInt(10, 20)
        const results = []
        for (let i = 0; i < COUNT; i++) {
            results.push({
                id: 71,
                name: `ttt${i}`,
                port: 80,
                uri: '/test1',
                frequency: 60,
                http_method: 'GET',
                http_body: {},
                version: 'v3',
                uri_fields_info: '',
                uri_data_clean: '',
                metric_type: '',
                const_labels: {},
                timeout: 30,
                status: '',
                http_headers: {},
                permissions: {
                    edit: true,
                    create: true,
                    delete: true,
                    use: true
                }
            })
        }
        return {
            // // statusCode: 500,
            // code: 2,
            // message: '获取metric列表成功',
            // data: results,
            // request_id: '13b87752ab28e7f97ee43cf87beb3413',
            // permissions: {create: true}
            code: 400,
            // message: ['chart blueking-nginx-ingress has been initialized in namespace test-ter', '222'],
            message: {
                name: '名称必填',
                port: '端口在1-8080内'
            },
            message: {
                name: '名称必填',
                port: ['端口在1-8080内', '22222']
            },
            data: null,
            request_id: '4c5d4429c7d3f1c8ebfecd2547c82dd9'
        }
    }
    return {
        code: 0,
        data: {}
    }
}

