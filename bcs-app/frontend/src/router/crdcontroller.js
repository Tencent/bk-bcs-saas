/**
 * @file crdcontroller router 配置
 */

const Index = () => import(/* webpackChunkName: 'network' */'@open/views/crdcontroller/index.vue')
const DBList = () => import(/* webpackChunkName: 'network' */'@open/views/crdcontroller/db_list.vue')
const LogList = () => import(/* webpackChunkName: 'network' */'@open/views/crdcontroller/log_list.vue')
const Detail = () => import(/* webpackChunkName: 'network' */'@open/views/crdcontroller/detail.vue')
const BcsPolaris = () => import(/* webpackChunkName: 'network' */'@open/views/crdcontroller/polaris_list.vue')

const childRoutes = [
    {
        path: 'crdcontroller/DbPrivilege',
        name: 'dbCrdcontroller',
        component: Index,
        meta: {
            crdKind: 'DbPrivilege'
        }
    },

    {
        path: 'crdcontroller/BcsLog',
        name: 'logCrdcontroller',
        component: Index,
        meta: {
            crdKind: 'BcsLog'
        }
    },

    {
        path: 'cluster/:clusterId/crdcontroller/DbPrivilege/instances',
        name: 'crdcontrollerDBInstances',
        component: DBList
    },

    {
        path: 'cluster/:clusterId/crdcontroller/BcsPolaris/instances',
        name: 'crdcontrollerPolarisInstances',
        component: BcsPolaris
    },

    {
        path: 'cluster/:clusterId/crdcontroller/BcsLog/instances',
        name: 'crdcontrollerLogInstances',
        component: LogList
    },

    {
        path: 'cluster/:clusterId/crdcontroller/:name/instances/:id',
        name: 'crdcontrollerInstanceDetail',
        component: Detail
    }
]

export default childRoutes
