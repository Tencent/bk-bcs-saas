/**
 * @file cluster all
 * @author ielgnaw <wuji0223@gmail.com>
 */

import moment from 'moment'
import faker from 'faker'

import {randomInt, sleep} from '../util'

export async function response(getArgs, postArgs, req) {
    const invoke = getArgs.invoke

    if (invoke === 'getAllNamespaceList') {
        const PROD_COUNT = 5
        const DEV_COUNT = 50
        const TEST_COUNT = 100

        const prod = {
            name: 'prod',
            environment: 'prod',
            environment_name: 'prod',
            results: []
        }

        const dev = {
            name: 'dev',
            environment: 'stag',
            environment_name: '测试',
            results: []
        }

        const test = {
            name: 'test',
            environment: 'test',
            environment_name: 'test',
            results: []
        }

        for (let i = 0; i < PROD_COUNT; i++) {
            prod.results.push(
                {
                    cluster_id: 'BCS-K8S-15007',
                    created_at: '2019-03-06T16:15:44+08:00',
                    creator: 'joelei',
                    description: '',
                    env_type: 'prod',
                    id: i,
                    name: `${i}prodprodprodprodprodprodprod${i}`,
                    project_id: 'b37778ec757544868a01e1f01f07037f',
                    status: '',
                    updated_at: '2019-03-06T16:15:44+08:00',
                    ns_vars: [
                        {
                            id: 92,
                            key: 'CLUB_NAME_WHITELIST',
                            name: 'CLUB_NAME_WHITELIST',
                            value: 'a-zA-Z 0-9!?#%&+\\x{4E00}-\\x{62FF}\\x{6300}-\\x{77FF}\\x{7800}-\\x{8CFF}\\x{8D00}-\\x{9FFF}'
                        },
                        {
                            id: 78,
                            key: 'test1',
                            name: 'test1',
                            value: '2'
                        }
                    ],
                    cluster_name: 'demosgddda12223',
                    environment: 'prod',
                    permissions: {
                        edit: true,
                        use: true,
                        view: true
                    }
                }
            )
        }

        for (let i = 0; i < DEV_COUNT; i++) {
            dev.results.push(
                {
                    cluster_id: 'BCS-K8S-15007',
                    created_at: '2019-03-06T16:15:44+08:00',
                    creator: 'joelei',
                    description: '',
                    env_type: 'dev',
                    id: i,
                    name: `${i}devdevdevdevdevdevdev${i}`,
                    project_id: 'b37778ec757544868a01e1f01f07037f',
                    status: '',
                    updated_at: '2019-03-06T16:15:44+08:00',
                    ns_vars: [
                        {
                            id: 92,
                            key: 'CLUB_NAME_WHITELIST',
                            name: 'CLUB_NAME_WHITELIST',
                            value: 'a-zA-Z 0-9!?#%&+\\x{4E00}-\\x{62FF}\\x{6300}-\\x{77FF}\\x{7800}-\\x{8CFF}\\x{8D00}-\\x{9FFF}'
                        },
                        {
                            id: 78,
                            key: 'test1',
                            name: 'test1',
                            value: '2'
                        }
                    ],
                    cluster_name: 'demosgddda12223',
                    environment: 'dev',
                    permissions: {
                        edit: true,
                        use: true,
                        view: true
                    }
                }
            )
        }

        for (let i = 0; i < TEST_COUNT; i++) {
            test.results.push(
                {
                    cluster_id: 'BCS-K8S-15007',
                    created_at: '2019-03-06T16:15:44+08:00',
                    creator: 'joelei',
                    description: '',
                    env_type: 'test',
                    id: i,
                    name: `${i}testtesttesttesttesttesttest${i}`,
                    project_id: 'b37778ec757544868a01e1f01f07037f',
                    status: '',
                    updated_at: '2019-03-06T16:15:44+08:00',
                    ns_vars: [
                        {
                            id: 92,
                            key: 'CLUB_NAME_WHITELIST',
                            name: 'CLUB_NAME_WHITELIST',
                            value: 'a-zA-Z 0-9!?#%&+\\x{4E00}-\\x{62FF}\\x{6300}-\\x{77FF}\\x{7800}-\\x{8CFF}\\x{8D00}-\\x{9FFF}'
                        },
                        {
                            id: 78,
                            key: 'test1',
                            name: 'test1',
                            value: '2'
                        }
                    ],
                    cluster_name: 'demosgddda12223',
                    environment: 'test',
                    permissions: {
                        edit: true,
                        use: true,
                        view: true
                    }
                }
            )
        }

        const data = []

        if (PROD_COUNT) {
            data.push(prod)
        }
        if (DEV_COUNT) {
            data.push(dev)
        }
        if (TEST_COUNT) {
            data.push(test)
        }

        return {
            code: 0,
            message: '取Namespace成功',
            data: data,
            request_id: 'a3d39fe931a75ca99af73507cb4f1072',
            permissions: {
                create: true
            }
        }
    }
    return {
        code: 0,
        data: {}
    }
}

