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

package apis

import (
	"bcs_cc/storage/models"
	"bcs_cc/utils"

	"github.com/gin-gonic/gin"
	"github.com/mitchellh/mapstructure"
	"github.com/tuvistavie/structomap"
)

// NamespaceList :
func NamespaceList(c *gin.Context) {
	// get project id、cluster id and project kind
	projectID, clusterID, projectKind, err := projectIDKindAndClusterID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	data := new(namespaceListForm)
	if err := BindForm(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	data.setDefaultLimit()

	filter := models.NamespaceFilterParams{
		ProjectID:     projectID,
		ClusterID:     clusterID,
		DesireAllData: data.DesireAllData,
		Limit:         data.Limit,
		Offset:        data.Offset,
	}
	// handle the k8s/mesos namespace list by project kind
	var nsList []map[string]interface{}
	var count int
	if projectKind != mesosKind {
		nsList, count, err = models.K8SNamespaceList(filter)
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	} else {
		nsList, count, err = models.MesosNamespaceList(filter)
		if err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	}
	utils.OKJSONResponse(c, map[string]interface{}{"count": count, "results": nsList})
}

func getProjectKind(projectID string) (uint, error) {
	project := &models.Project{ProjectID: projectID}
	if err := project.RetriveRecord(); err != nil {
		return 0, err
	}
	return project.Kind, nil
}

// NamespaceInfo : get a namespace detail info
func NamespaceInfo(c *gin.Context) {
	// get project id, project kind and cluster id
	projectID, clusterID, projectKind, err := projectIDKindAndClusterID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	nsID, err := transferNSID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// separation the k8s/mesos
	var nsInfo map[string]interface{}
	if projectKind != mesosKind {
		namespace := &models.KubernetesNamespace{Model: models.Model{ID: nsID}, ProjectID: projectID, ClusterID: clusterID}
		if err := namespace.RetriveRecord(); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		serializer := structomap.New().UseSnakeCase().PickAll()
		serializer = serializer.Pick("CreatedAt", "UpdatedAt", "ID").Omit("Model")
		nsInfo = serializer.Transform(namespace)
	} else {
		namespace := &models.Namespace{Model: models.Model{ID: nsID}, ProjectID: projectID, ClusterID: clusterID}
		if err := namespace.RetriveRecord(); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		serializer := structomap.New().UseSnakeCase().PickAll()
		serializer = serializer.Pick("CreatedAt", "UpdatedAt", "ID").Omit("Model")
		nsInfo = serializer.Transform(namespace)
	}
	// return the namespace detail info
	utils.OKJSONResponse(c, nsInfo)
}

// DeleteNamespace : delete a namespace record
func DeleteNamespace(c *gin.Context) {
	projectID, clusterID, projectKind, err := projectIDKindAndClusterID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// transfer namespace id
	nsID, err := transferNSID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// separate the k8s/mesos
	if projectKind != mesosKind {
		namespace := &models.KubernetesNamespace{Model: models.Model{ID: nsID}, ProjectID: projectID, ClusterID: clusterID}
		if err := namespace.DeleteRecord(); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	} else {
		namespace := &models.Namespace{Model: models.Model{ID: nsID}, ProjectID: projectID, ClusterID: clusterID}
		if err := namespace.DeleteRecord(); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	}
	utils.OKJSONResponseWithMessage(c, nil, "Namespace successfully deleted")
}

// DeleteClusterNamespaces : delete all namespace in specific cluster
func DeleteClusterNamespaces(c *gin.Context) {
	// get project id、cluster id and project kind
	projectID, clusterID, projectKind, err := projectIDKindAndClusterID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// separate the k8s/mesos
	if projectKind != mesosKind {
		if err := models.DeleteK8SClusterNamespaces(projectID, clusterID); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	} else {
		if err := models.DeleteMesosClusterNamespaces(projectID, clusterID); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
	}

	utils.OKJSONResponseWithMessage(c, nil, "Namespace successfully deleted")
}

// CreateNamespace : create namespace record
func CreateNamespace(c *gin.Context) {
	// get project id、cluster id and project kind
	projectID, clusterID, projectKind, err := projectIDKindAndClusterID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// verify data
	data := new(createNamespaceDataJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	if err := models.ValidateProjectCluster(projectID, clusterID); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	// separate the k8s/mesos
	if projectKind != mesosKind {
		namespace := &models.KubernetesNamespace{ProjectID: projectID, ClusterID: clusterID}
		if err := mapstructure.Decode(data, &namespace); err != nil {
			utils.BadReqJSONResponse(c, err)
			return
		}
		if err := namespace.CreateRecord(); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		utils.OKJSONResponse(c, namespace)
	} else {
		namespace := &models.Namespace{ProjectID: projectID, ClusterID: clusterID}
		if err := mapstructure.Decode(data, &namespace); err != nil {
			utils.BadReqJSONResponse(c, err)
			return
		}
		if err := namespace.CreateRecord(); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		utils.OKJSONResponse(c, namespace)
	}
}

// UpdateNamespace :
func UpdateNamespace(c *gin.Context) {
	// get project id、cluster id and project kind
	projectID, clusterID, projectKind, err := projectIDKindAndClusterID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// transfer namespace id
	nsID, err := transferNSID(c)
	if err != nil {
		utils.BadReqJSONResponse(c, err)
		return
	}
	// verify data
	data := new(updateNamespaceDataJSON)
	if err := BindJSON(c, data); err != nil {
		utils.BadReqJSONResponse(c, ValidationError(err))
		return
	}
	if err := models.ValidateProjectCluster(projectID, clusterID); err != nil {
		utils.DBErrorResponse(c, err)
		return
	}
	imageSecretExist := false
	if data.HasImageSecret != nil {
		imageSecretExist = true
	}
	// separate the k8s/mesos
	if projectKind != mesosKind {
		namespace := models.KubernetesNamespace{ProjectID: projectID, ClusterID: clusterID, Model: models.Model{ID: nsID}}
		if err := mapstructure.Decode(data, &namespace); err != nil {
			utils.BadReqJSONResponse(c, err)
			return
		}
		updater := &models.K8SNamespaceUpdate{Namespace: &namespace, ImageSecretExist: imageSecretExist}
		if err := updater.UpdateRecord(); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		utils.OKJSONResponse(c, updater.Namespace)
	} else {
		namespace := models.Namespace{ProjectID: projectID, ClusterID: clusterID, Model: models.Model{ID: nsID}}
		if err := mapstructure.Decode(data, &namespace); err != nil {
			utils.BadReqJSONResponse(c, err)
			return
		}
		updater := &models.MesosNamespaceUpdate{Namespace: &namespace, ImageSecretExist: imageSecretExist}
		if err := updater.UpdateRecord(); err != nil {
			utils.DBErrorResponse(c, err)
			return
		}
		utils.OKJSONResponse(c, updater.Namespace)
	}
}

func projectIDKindAndClusterID(c *gin.Context) (string, string, uint, error) {
	// get project id and cluster id
	projectID, clusterID, err := getProjectIDClusterIDFromContext(c)
	if err != nil {
		return "", "", 0, err
	}
	// get kind of project
	projectKind, err := getProjectKind(projectID)
	if err != nil {
		return projectID, clusterID, 0, err
	}
	return projectID, clusterID, projectKind, nil
}

func transferNSID(c *gin.Context) (uint, error) {
	nsIDStr := c.Params.ByName("namespace_id")
	nsIDInt, err := utils.String2Int(nsIDStr)
	if err != nil {
		return 0, err
	}
	return uint(nsIDInt), nil
}
