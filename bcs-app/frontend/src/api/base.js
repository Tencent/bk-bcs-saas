import { request } from './request'

// app
export const projectFeatureFlag = request('get', '/api/projects/$projectId/clusters/$clusterId/feature_flags/')

// log
export const stdLogs = request('get', '/api/logs/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/pods/$podId/stdlogs/')
export const stdLogsDownload = request('get', '/api/logs/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/pods/$podId/stdlogs/download/')
export const stdLogsSession = request('post', '/api/logs/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/pods/$podId/stdlogs/sessions/')

// dashbord
export const dashbordList = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/$type/$category/')
export const retrieveDetail = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/$type/$category/$name/')
export const retrieveContainerDetail = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/$category/$name/containers/$containerName/')
export const podMetric = request('post', '/api/metrics/projects/$projectId/clusters/$clusterId/pods/$metric/')
export const containerMetric = request('post', '/api/metrics/projects/$projectId/clusters/$clusterId/pods/$podId/containers/$metric/')
export const listWorkloadPods = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/pods/')
export const listStoragePods = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/pods/$podId/$type/')
export const listContainers = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/pods/$podId/containers/')
export const fetchContainerEnvInfo = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/pods/$podId/containers/$containerName/env_info/')
export const resourceCreate = request('post', '/api/dashboard/projects/$projectId/clusters/$clusterId/$type/$category/')
export const resourceUpdate = request('put', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/$type/$category/$name/')
export const resourceDelete = request('delete', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/$type/$category/$name/')
export const exampleManifests = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/examples/manifests/')

// apply hosts
export const getBizMaintainers = request('get', '/api/projects/$projectId/biz_maintainers/')

// application
export const sourceExpansion = request('put', '/api/app/mesos/projects/$projectId/clusters/$clusterId/namespaces/$namespace/instances/$application/')

// node
export const getK8sNodes = request('get', '/api/cluster_mgr/projects/$projectId/clusters/$clusterId/nodes/')
export const fetchK8sNodeLabels = request('post', '/api/cluster_mgr/projects/$projectId/clusters/$clusterId/nodes/labels/')
export const setK8sNodeLabels = request('put', '/api/cluster_mgr/projects/$projectId/clusters/$clusterId/nodes/labels/')
export const getNodeTaints = request('post', '/api/cluster_mgr/projects/$projectId/clusters/$clusterId/nodes/taints/')
export const setNodeTaints = request('put', '/api/cluster_mgr/projects/$projectId/clusters/$clusterId/nodes/taints/')

export default {
    stdLogs,
    stdLogsDownload,
    stdLogsSession,
    dashbordList,
    projectFeatureFlag,
    getBizMaintainers,
    podMetric,
    containerMetric,
    retrieveDetail,
    listWorkloadPods,
    listStoragePods,
    listContainers,
    retrieveContainerDetail,
    fetchContainerEnvInfo,
    getK8sNodes,
    fetchK8sNodeLabels,
    setK8sNodeLabels,
    resourceCreate,
    resourceUpdate,
    resourceDelete,
    exampleManifests,
    getNodeTaints,
    setNodeTaints
}
