package models

// DeleteUnscoped :
func (qs ManagerMasterQuerySet) DeleteUnscoped() error {
	return qs.db.Unscoped().Delete(ManagerMaster{}).Error
}

// ClusterIDInWithoutError : when length of clusterIDList is 0, return qs all
func (qs ManagerMasterQuerySet) ClusterIDInWithoutError(filterWithClusterID bool, clusterIDList ...string) ManagerMasterQuerySet {
	if len(clusterIDList) == 0 && !filterWithClusterID {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("cluster_id IN (?)", clusterIDList))
}

// ProjectIDEqWithNull : return all public cluster
func (qs ManagerMasterQuerySet) ProjectIDEqWithNull(projectID string) ManagerMasterQuerySet {
	if projectID == "" || projectID == "null" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("project_id = ?", projectID))
}

type clusterMasterFunctionType func(ManagerMasterQuerySet, string, string) ManagerMasterQuerySet

// ClusterMasterFilter : filter with field
func (qs ManagerMasterQuerySet) ClusterMasterFilter(fields map[string]string, f clusterMasterFunctionType) ManagerMasterQuerySet {
	for field, val := range fields {
		if val == "" || val == "null" {
			continue
		}
		qs = f(qs, field, val)
	}
	return qs
}

// function for query
func masterFilterString(qs ManagerMasterQuerySet, field string, val string) ManagerMasterQuerySet {
	switch field {
	case "project_id":
		return qs.ProjectIDEq(val)
	case "cluster_id":
		return qs.ClusterIDEq(val)
	case "inner_ip":
		return qs.InnerIPEq(val)
	}
	return qs
}

// SetInstanceIDWithoutEmpty : update instance id
func (u ManagerMasterUpdater) SetInstanceIDWithoutEmpty(instanceID string) ManagerMasterUpdater {
	if instanceID == "" {
		return u
	}
	u.fields[string(ManagerMasterDBSchema.InstanceID)] = instanceID
	return u
}
