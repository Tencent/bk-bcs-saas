import { request } from './request'

// app
export const projectFeatureFlag = request('get', '/api/projects/$projectId/clusters/$clusterId/feature_flags/')

// log
export const stdLogs = request('get', '/api/logs/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/pods/$podId/stdlogs/')
export const stdLogsDownload = request('get', '/api/logs/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/pods/$podId/stdlogs/download/')
export const stdLogsSession = request('post', '/api/logs/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/pods/$podId/stdlogs/sessions/')

// dashbord
export const dashbordList = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/$type/$category/')
export const retrieveDetail = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/$category/$name/')
export const retrieveContainerDetail = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/$category/$name/containers/$containerName/')
export const podMetric = request('post', '/api/metrics/projects/$projectId/clusters/$clusterId/pods/$metric/')
export const containerMetric = request('post', '/api/metrics/projects/$projectId/clusters/$clusterId/pods/$podId/containers/$metric/')
export const listWorkloadPods = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/pods/')
export const listStoragePods = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/pods/$podId/$type/')
export const listContainers = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/pods/$podId/containers/')
export const fetchContainerEnvInfo = request('get', '/api/dashboard/projects/$projectId/clusters/$clusterId/namespaces/$namespaceId/workloads/pods/$podId/containers/$containerName/env_info/')

// apply hosts
export const getBizMaintainers = request('get', '/api/projects/$projectId/biz_maintainers/')

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
    fetchContainerEnvInfo
}
