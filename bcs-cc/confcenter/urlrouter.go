/*
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

package confcenter

import (
	"github.com/gin-gonic/gin"

	"bcs-cc/confcenter/apis"
)

// URLConf : api router
func URLConf(engine *gin.Engine) {
	engine.Use(RequestLogMiddleware())

	healthz := engine.Group("/healthz")
	{
		healthz.GET("/", apis.Healthz)
	}

	area := engine.Group("/areas")
	area.Use(JWTTokenMiddleware())
	{
		area.GET("/", apis.AreaListInfo)
		area.POST("/", apis.CreateArea)
		area.GET("/:id/", apis.AreaInfo)
		area.PUT("/:id/", apis.UpdateArea)
	}

	project := engine.Group("/projects")
	project.Use(JWTTokenMiddleware())
	{
		project.GET("/", apis.ProjectListInfo)
		project.POST("/", apis.CreateProject)
		project.GET("/:project_id/", apis.ProjectInfo)
		project.PUT("/:project_id/", apis.UpdateProject)
	}
	projectList := engine.Group("/project_list")
	projectList.Use(JWTTokenMiddleware())
	{
		projectList.POST("/", apis.ProjectsListEx)
	}

	authproject := engine.Group("/auth_projects")
	authproject.Use(JWTTokenMiddleware())
	{
		authproject.GET("/", apis.ProjectListInfoWithAuth)
	}
	clusterConfigure := engine.Group("/v1/configure/clusters")
	authproject.Use(JWTTokenMiddleware())
	{
		clusterConfigure.POST("/", apis.CreateClusterBaseVersion)
		clusterConfigure.PUT("/", apis.UpdateClusterBaseVersion)
	}
	clusterVersion := engine.Group("/v1/clusters/:cluster_id/cluster_version_config")
	authproject.Use(JWTTokenMiddleware())
	{
		clusterVersion.GET("/", apis.VersionConfig)
		clusterVersion.POST("/", apis.CreateClusterSnapshot)
	}
	allMaster := engine.Group("/v1/masters")
	{
		allMaster.GET("/all_master_list/", apis.MasterListByType)
		allMaster.GET("/list/", apis.MasterListByType)
	}

	master := engine.Group("/projects/:project_id/clusters/:cluster_id")
	master.Use(JWTTokenMiddleware())
	{
		master.GET("/manager_masters/", apis.FetchMasterList)
		master.POST("/manager_masters/", apis.CreateMaster)
		master.PUT("/manager_masters/", apis.UpdateMaster)
		master.POST("/batch_manager_masters/", apis.BatchCreateMaster)
		master.PUT("/replace_manager_masters/", apis.ReplaceMaster)
		master.DELETE("/master/", apis.DeleteMaster)
	}

	cluster := engine.Group("/projects/:project_id/clusters")
	cluster.Use(JWTTokenMiddleware())
	{
		cluster.GET("/", apis.ClusterList)
		cluster.POST("/", apis.CreateCluster)
		cluster.GET("/:cluster_id/", apis.ClusterInfo)
		cluster.GET("/:cluster_id/related/areas/", apis.ClusterAreaInfo)
		cluster.GET("/:cluster_id/history_data/", apis.ClusterHistoryData)
		cluster.PUT("/:cluster_id/", apis.UpdateCluster)
		cluster.DELETE("/:cluster_id/", apis.DeleteCluster)
	}
	engine.GET("/clusters/:cluster_id/related/areas/info/", apis.ClusterAreaInfo)

	ipRelatedCluster := engine.Group("/ip_related_cluster_info")
	ipRelatedCluster.Use(JWTTokenMiddleware())
	{
		ipRelatedCluster.GET("/:ip/", apis.GetClusterByIP)
	}

	clusterList := engine.Group("/projects/:project_id/clusters_list")
	clusterList.Use(JWTTokenMiddleware())
	{
		clusterList.POST("/", apis.ClustersListEx)
		clusterList.GET("/", apis.GetAllClusterList)
	}

	nodeList := engine.Group("/projects/:project_id/nodes")
	nodeList.Use(JWTTokenMiddleware())
	{
		nodeList.PUT("/", apis.UpdateNodeList)
	}

	node := engine.Group("/projects/:project_id/clusters/:cluster_id")
	node.Use(JWTTokenMiddleware())
	{
		node.GET("/nodes/", apis.NodeList)
		node.POST("/nodes/", apis.CreateNode)
		node.PATCH("/nodes/", apis.BatchOperateNodes)
		node.GET("/nodes/:node_id/", apis.NodeInfo)
		node.PUT("/nodes/:node_id/", apis.UpdateNode)
	}

	namespace := engine.Group("/projects/:project_id/clusters/:cluster_id")
	namespace.Use(JWTTokenMiddleware())
	{
		namespace.GET("/namespaces/", apis.NamespaceList)
		namespace.POST("/namespaces/", apis.CreateNamespace)
		namespace.GET("/namespaces/:namespace_id/", apis.NamespaceInfo)
		namespace.PUT("/namespaces/:namespace_id/", apis.UpdateNamespace)
		namespace.DELETE("/namespaces/:namespace_id/", apis.DeleteNamespace)
		namespace.DELETE("/batch_delete_namespaces/", apis.DeleteClusterNamespaces)
	}

	zkConfig := engine.Group("/zk_config")
	zkConfig.Use(JWTTokenMiddleware())
	{
		zkConfig.GET("/", apis.ZKConfig)
	}

	nodesWithVersion := engine.Group("/v1/nodes")
	{
		nodesWithVersion.GET("/all_node_list/", apis.GetAllNodeList)
		nodesWithVersion.GET("/list/", apis.GetAllNodeList)
	}

	projectResource := engine.Group("/v1/projects/resource")
	projectResource.Use(JWTTokenMiddleware())
	{
		projectResource.GET("/", apis.ProjectsResource)
	}

	clusterVersionConfig := engine.Group("/v1/all/clusters/version_config")
	{
		clusterVersionConfig.GET("/", apis.ClusterVersionConfig)
	}

	clusters := engine.Group("/clusters/:cluster_id")
	clusters.Use(JWTTokenMiddleware())
	{
		clusters.GET("/", apis.GetClusterByClusterID)
	}
}
