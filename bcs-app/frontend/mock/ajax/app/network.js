/**
 * @file cluster all
 * @author ielgnaw <wuji0223@gmail.com>
 */

// import moment from 'moment'
// import faker from 'faker'

// import { randomInt, sleep } from '../util'

module.exports = {
    response: async function response (getArgs, postArgs, req) {
        console.log('req', req.method)
        console.log('getArgs', getArgs)
        console.log('postArgs', postArgs)
        const invoke = getArgs.invoke
        if (invoke === 'runCloudLoadBalance') {
            const data = {
                "data": {},
                "code": 0,
                "message": "OK",
                "request_id": "27fda112a04b45d8a49075b92641a976"
            }
            return data
        } else if (invoke === 'stopCloudLoadBalance') {
            const data = {
                "data": {},
                "code": 0,
                "message": "OK",
                "request_id": "27fda112a04b45d8a49075b92641a976"
            }
            return data
        }
        if (invoke === 'updateCloudLoadBalance') {
            const data = {
                "data": {
                    "id": 2,
                    "project_id": "ab2b254938e84f6b86b466cc22e730b1",
                    "cluster_id": "BCS-MESOS-10024",
                    "namespace": "bcs-system",
                    "clb_name": "test123",
                    "resource_name": "test123-e4mZl1",
                    "region": "ap_shanghai",
                    "image": "/paas/public/bcs/clb-controller:0.2.2",
                    "status": "not_created",
                    "vpc_id": "test123",
                    "network_type": "overlay",
                    "clb_type": "private",
                    "svc_discovery_type": "custom",
                    "clb_project_id": 0,
                    "metric_port": 59050,
                    "implement_type": "sdk",
                    "backend_type": "cvm"
                },
                "code": 0,
                "message": "OK",
                "request_id": "27fda112a04b45d8a49075b92641a976"
            }
            return data
        } else if (invoke === 'getCloudLoadBalanceDetail') {
            const data = {
                "data": {
                    "id": 1,
                    "project_id": "ab2b254938e84f6b86b466cc22e730b1",
                    "cluster_id": "BCS-MESOS-10038",
                    "namespace": "bcs-system",
                    "clb_name": "test123",
                    "resource_name": "test123-1apT8y",
                    "region": "ap_shanghai",
                    "image": "/paas/public/bcs/clb-controller:0.2.2",
                    "status": "not_created",
                    "vpc_id": "test123",
                    "network_type": "overlay",
                    "clb_type": "private",
                    "svc_discovery_type": "custom",
                    "clb_project_id": 0,
                    "clb_status": "ssss",
                    "metric_port": 59050,
                    "implement_type": "sdk",
                    "backend_type": "cvm"
                },
                "code": 0,
                "message": "OK",
                "request_id": "d007ed43eb9041c9a871d6fbca25b857"
            }
            return data
        } else if (invoke === 'getCloudLoadBalanceList') {
            const COUNT = 12
            const data = {
                "data": [
                    {
                        "id": 1,
                        "project_id": "ab2b254938e84f6b86b466cc22e730b1",
                        "cluster_id": "BCS-MESOS-10038",
                        "namespace": "bcs-system",
                        "clb_name": "test123",
                        "resource_name": "test123-1apT8y",
                        "region": "ap_shanghai",
                        "image": "/paas/public/bcs/clb-controller:0.2.2",
                        "status": "not_created",
                        "vpc_id": "test123",
                        "network_type": "overlay",
                        "clb_type": "private",
                        "svc_discovery_type": "custom",
                        "clb_project_id": 0,
                        "metric_port": 59050,
                        "implement_type": "sdk",
                        "backend_type": "cvm"
                    },
                    {
                        "id": 2,
                        "project_id": "ab2b254938e84f6b86b466cc22e730b1",
                        "cluster_id": "BCS-MESOS-10038",
                        "namespace": "bcs-system",
                        "clb_name": "test12322",
                        "resource_name": "test123-e4mZl1",
                        "region": "ap_shanghai",
                        "image": "/paas/public/bcs/clb-controller:0.2.2",
                        "status": "not_created",
                        "vpc_id": "test123",
                        "network_type": "overlay",
                        "clb_type": "private",
                        "svc_discovery_type": "custom",
                        "clb_project_id": 0,
                        "metric_port": 59050,
                        "implement_type": "sdk",
                        "backend_type": "cvm",
                        "clb_status": "failed",
                        "clb_message": "xxx"
                    }
                ],
                "code": 0,
                "message": "OK",
                "request_id": "421cf6d4cb764e5c834aa5f9a5dce37c"
            }

            return data
        }
        return {
            code: 0,
            data: {}
        }
    }
}
