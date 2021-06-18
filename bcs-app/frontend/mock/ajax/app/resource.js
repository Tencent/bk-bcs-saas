/**
 * @file cluster all
 * @author ielgnaw <wuji0223@gmail.com>
 */

// import moment from 'moment'
// import faker from 'faker'

// import { randomInt, sleep } from '../util'

export async function response (getArgs, postArgs, req) {
    console.log('req', req.method)
    console.log('getArgs', getArgs)
    console.log('postArgs', postArgs)
    const invoke = getArgs.invoke
    if (invoke === 'getIngressList') {
        const COUNT = 12
        const data = []

        for (let i = 0; i < COUNT; i++) {
            data.push({
                can_delete: true,
                can_delete_msg: '',
                can_update: true,
                can_update_msg: '',
                clusterId: 'BCS-K8S-25023',
                cluster_id: 'BCS-K8S-25023',
                cluster_name: '蓝盾公共集群-深圳',
                createTime: '2019-01-25 11:41:09',
                create_time: '2019-01-25T11:41:09.577+08:00',
                creator: 'familiang',
                data: {
                    datas: {},
                    metadata: {
                        labels: {
                            'io.tencent.bcs.app.appid': '100148',
                            'io.tencent.bcs.cluster': 'BCS-K8S-25023',
                            'io.tencent.bcs.clusterid': 'BCS-K8S-25023',
                            'io.tencent.bcs.kind': 'Kubernetes',
                            'io.tencent.bcs.namespace': 'fami-test',
                            'io.tencent.bkdata.baseall.dataid': '6566',
                            'io.tencent.bkdata.container.stdlog.dataid': '10048',
                            'io.tencent.paas.instanceid': '11435',
                            'io.tencent.paas.projectid': '3f4e1f7616fa49b7891fb809b19ab23f',
                            'io.tencent.paas.source_type': 'template',
                            'io.tencent.paas.templateid': '515',
                            'io.tencent.paas.version': '0109',
                            'io.tencent.paas.versionid': '7543'
                        }
                    },
                    spec: {}
                },
                environment: 'debug',
                instance_id: 11435,
                name: 'ingress-config',
                namespace: 'fami-test',
                namespace_id: 1865,
                permissions: {
                    edit: false,
                    use: true,
                    view: true
                },
                resourceName: `ingress-config${i}`,
                resourceType: 'Ingress',
                source_type: '模板集',
                status: 'Running',
                updateTime: '2019-01-25T11:41:55.883+08:00',
                update_time: '2019-01-25 11:41:08',
                updator: 'familiang',
                _id: '5c4a8555f22e15d992762b47'
            })
        }

        return {
            code: 0,
            data: {
                data: data,
                length: COUNT
            },
            message: 'ok'
        }
    }
    return {
        code: 0,
        data: {}
    }
}
