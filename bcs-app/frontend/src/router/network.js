/**
 * @file network router 配置
 */

const Service = () => import(/* webpackChunkName: 'network' */'@open/views/network/service')
const LoadBalance = () => import(/* webpackChunkName: 'network' */'@open/views/network/loadbalance')
const CloudLoadBalance = () => import(/* webpackChunkName: 'network' */'@open/views/network/cloudloadbalance')
const LoadBalanceDetail = () => import(/* webpackChunkName: 'network' */'@open/views/network/loadbalance-detail')
const CloudLoadBalanceDetail = () => import(/* webpackChunkName: 'network' */'@open/views/network/cloudloadbalance-detail')
const childRoutes = [
    {
        path: ':projectCode/service',
        name: 'service',
        component: Service
    },
    {
        path: ':projectCode/loadbalance',
        name: 'loadBalance',
        component: LoadBalance
    },
    {
        path: ':projectCode/cloudloadbalance',
        name: 'cloudLoadBalance',
        component: CloudLoadBalance
    },
    {
        path: ':projectCode/cluster/:clusterId/namespace/:namespace/loadbalance/:lbId/detail',
        name: 'loadBalanceDetail',
        component: LoadBalanceDetail
    },
    {
        path: ':projectCode/cloudloadbalance/:instanceId/detail/:instanceName/:instanceNamespace/:instanceCategory',
        name: 'cloudLoadBalanceDetail',
        component: CloudLoadBalanceDetail
    }
]

export default childRoutes
