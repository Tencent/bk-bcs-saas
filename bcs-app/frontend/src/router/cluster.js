/**
 * @file cluster router 配置
 */

// 集群首页
const Cluster = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster')
// 创建集群
const ClusterCreate = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/create')
// 外部版创建集群
const ClusterCreateExternal = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/create.external')
// 集群总览
const ClusterOverview = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/overview')
// 节点详情
const ClusterNode = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/node')
// 集群信息
const ClusterInfo = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/info')
const ClusterNodeOverview = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/node-overview')
const ContainerDetailForNode = () => import(/* webpackChunkName: 'cluster' */'@open/views/cluster/container')

const childRoutes = [
    {
        path: '',
        redirect: {
            name: 'clusterMain'
        }
    },
    // domain/bcs/projectId => domain/bcs/projectCode/cluster 容器服务的首页是具体项目的集群页面
    // 集群首页
    {
        path: 'cluster',
        name: 'clusterMain',
        component: Cluster
    },
    // 创建集群
    {
        path: 'cluster/create',
        name: 'clusterCreate',
        component: global.REGION === 'ieod' ? ClusterCreate : ClusterCreateExternal,
        meta: {
            menuId: 'CLUSTER'
        }
    },
    // 集群总览
    {
        path: 'cluster/:clusterId/overview',
        name: 'clusterOverview',
        component: ClusterOverview,
        alias: 'cluster/:clusterId',
        meta: {
            menuId: 'CLUSTER'
        }
    },
    // 集群里的节点列表
    {
        path: 'cluster/:clusterId/node',
        name: 'clusterNode',
        component: ClusterNode,
        meta: {
            menuId: 'CLUSTER'
        }
    },
    // 集群里的集群信息
    {
        path: 'cluster/:clusterId/info',
        name: 'clusterInfo',
        component: ClusterInfo,
        meta: {
            menuId: 'CLUSTER'
        }
    },
    // 集群里的具体节点
    {
        path: 'cluster/:clusterId/node/:nodeId',
        name: 'clusterNodeOverview',
        component: ClusterNodeOverview,
        meta: {
            menuId: 'CLUSTER'
        }
    },
    // 节点详情页面跳转的容器详情页面
    {
        path: 'cluster/:clusterId/node/:nodeId/container/:containerId',
        name: 'containerDetailForNode',
        component: ContainerDetailForNode,
        meta: {
            menuId: 'CLUSTER'
        }
    }
]

export default childRoutes
