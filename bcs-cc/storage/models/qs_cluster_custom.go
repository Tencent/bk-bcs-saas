package models

// ClusterStatusInWithoutError : when length of status is 0, return qs all
func (qs ClusterQuerySet) ClusterStatusInWithoutError(statusList ...string) ClusterQuerySet {
	if len(statusList) == 0 || statusList[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("status IN (?)", statusList))
}

// ClusterStatusNotInWithoutError : when length of status is 0, return qs all
func (qs ClusterQuerySet) ClusterStatusNotInWithoutError(statusList ...string) ClusterQuerySet {
	if len(statusList) == 0 || statusList[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("status NOT IN (?)", statusList))
}

// ClusterTypeEqWithoutExist : when cluster type is not exist, return qs all
func (qs ClusterQuerySet) ClusterTypeEqWithoutExist(clusterType string) ClusterQuerySet {
	if clusterType == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("type = ?", clusterType))
}

// RelatedProjectsLike : return public cluster by related project
func (qs ClusterQuerySet) RelatedProjectsLike(projectID string) ClusterQuerySet {
	return qs.w(qs.db.Where("related_projects LIKE ?", "%%"+projectID+"%%"))
}

// RelatedProjectsNotNull : return all public cluster
func (qs ClusterQuerySet) RelatedProjectsNotNull() ClusterQuerySet {
	return qs.w(qs.db.Where("related_projects is not NULL").Where("related_projects != \"\""))
}

// ProjectIDEqWithEmpty : project is ""/"null"/real val
func (qs ClusterQuerySet) ProjectIDEqWithEmpty(projectID string) ClusterQuerySet {
	if projectID == "" || projectID == "null" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("project_id = ?", projectID))
}

// ClusterIDEqWithEmpty : cluster id is "" or "null"
func (qs ClusterQuerySet) ClusterIDEqWithEmpty(clusterID string) ClusterQuerySet {
	if clusterID == "" || clusterID == "null" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("cluster_id = ?", clusterID))
}

// NameEqWithEmpty : name is ""
func (qs ClusterQuerySet) NameEqWithEmpty(name string) ClusterQuerySet {
	if name == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("name = ?", name))
}

// ClusterIDInWithoutError : when length of status is 0, return qs all
func (qs ClusterQuerySet) ClusterIDInWithoutError(clusterIDList ...string) ClusterQuerySet {
	if len(clusterIDList) == 0 || clusterIDList[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("cluster_id IN (?)", clusterIDList))
}

// ClusterIDNotInWithoutError : when length of status is 0, return qs all
func (qs ClusterQuerySet) ClusterIDNotInWithoutError(clusterIDList ...string) ClusterQuerySet {
	if len(clusterIDList) == 0 {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("cluster_id NOT IN (?)", clusterIDList))
}

// ClusterListByProjectID : get the private and public cluster by project id
func (qs ClusterQuerySet) ClusterListByProjectID(projectID string) ClusterQuerySet {
	if projectID == "" || projectID == "null" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("project_id = ? OR related_projects LIKE ?", projectID, "%%"+projectID+"%%"))
}

//SetDisableWithoutNil :
func (u ClusterUpdater) SetDisableWithoutNil(disabled *bool) ClusterUpdater {
	if disabled == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.Disabled)] = *disabled
	return u
}

//SetAreaIDWithoutNil :
func (u ClusterUpdater) SetAreaIDWithoutNil(areaID *int) ClusterUpdater {
	if areaID == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.AreaID)] = *areaID
	return u
}

// SetConfigSvrCountWithoutNil :
func (u ClusterUpdater) SetConfigSvrCountWithoutNil(configSvrCount *int) ClusterUpdater {
	if configSvrCount == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.ConfigSvrCount)] = *configSvrCount
	return u
}

// SetMasterCountWithoutNil :
func (u ClusterUpdater) SetMasterCountWithoutNil(masterCount *int) ClusterUpdater {
	if masterCount == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.MasterCount)] = *masterCount
	return u
}

//SetNodeCountWithoutNil :
func (u ClusterUpdater) SetNodeCountWithoutNil(nodeCount *int) ClusterUpdater {
	if nodeCount == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.NodeCount)] = *nodeCount
	return u
}

// SetTotalCPUWithoutNil :
func (u ClusterUpdater) SetTotalCPUWithoutNil(totalCPU *float64) ClusterUpdater {
	if totalCPU == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.TotalCPU)] = *totalCPU
	return u
}

// SetTotalDiskWithoutNil :
func (u ClusterUpdater) SetTotalDiskWithoutNil(totalDisk *float64) ClusterUpdater {
	if totalDisk == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.TotalDisk)] = *totalDisk
	return u
}

// SetTotalMemWithoutNil :
func (u ClusterUpdater) SetTotalMemWithoutNil(totalMem *float64) ClusterUpdater {
	if totalMem == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.TotalMem)] = *totalMem
	return u
}

// SetRemainCPUWithoutNil :
func (u ClusterUpdater) SetRemainCPUWithoutNil(remainCPU *float64) ClusterUpdater {
	if remainCPU == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.RemainCPU)] = *remainCPU
	return u
}

// SetRemainDiskWithoutNil :
func (u ClusterUpdater) SetRemainDiskWithoutNil(remainDisk *float64) ClusterUpdater {
	if remainDisk == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.RemainDisk)] = *remainDisk
	return u
}

// SetRemainMemWithoutNil :
func (u ClusterUpdater) SetRemainMemWithoutNil(remainMem *float64) ClusterUpdater {
	if remainMem == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.RemainMem)] = *remainMem
	return u
}

// SetIPResourceTotalWithoutNil :
func (u ClusterUpdater) SetIPResourceTotalWithoutNil(iPResourceTotal *int) ClusterUpdater {
	if iPResourceTotal == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.IPResourceTotal)] = *iPResourceTotal
	return u
}

// SetIPResourceUsedWithoutNil :
func (u ClusterUpdater) SetIPResourceUsedWithoutNil(iPResourceUsed *int) ClusterUpdater {
	if iPResourceUsed == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.IPResourceUsed)] = *iPResourceUsed
	return u
}

// SetNotNeedNATWithoutNil :
func (u ClusterUpdater) SetNotNeedNATWithoutNil(needNAT *bool) ClusterUpdater {
	if needNAT == nil {
		return u
	}
	u.fields[string(ClusterDBSchema.NotNeedNAT)] = !(*needNAT)
	return u
}

// SetRelatedProjectsWithoutEmpty :
func (u ClusterUpdater) SetRelatedProjectsWithoutEmpty(relatedProjects string) ClusterUpdater {
	if relatedProjects == "" {
		return u
	}
	u.fields[string(ClusterDBSchema.RelatedProjects)] = relatedProjects
	return u
}

// SetNameWithoutEmpty :
func (u ClusterUpdater) SetNameWithoutEmpty(name string) ClusterUpdater {
	if name == "" {
		return u
	}
	u.fields[string(ClusterDBSchema.Name)] = name
	return u
}

// SetStatusWithoutEmpty :
func (u ClusterUpdater) SetStatusWithoutEmpty(status string) ClusterUpdater {
	if status == "" {
		return u
	}
	u.fields[string(ClusterDBSchema.Status)] = status
	return u
}
