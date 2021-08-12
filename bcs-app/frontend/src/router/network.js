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
        path: 'service',
        name: 'service',
        component: Service
    },
    {
        path: 'loadbalance',
        name: 'loadBalance',
        component: LoadBalance
    },
    {
        path: 'cloudloadbalance',
        name: 'cloudLoadBalance',
        component: CloudLoadBalance
    },
    {
        path: 'cluster/:clusterId/namespace/:namespace/loadbalance/:lbId/detail',
        name: 'loadBalanceDetail',
        component: LoadBalanceDetail
    },
    {
        path: 'cloudloadbalance/:instanceId/detail/:instanceName/:instanceNamespace/:instanceCategory',
        name: 'cloudLoadBalanceDetail',
        component: CloudLoadBalanceDetail
    }
]

export default childRoutes
