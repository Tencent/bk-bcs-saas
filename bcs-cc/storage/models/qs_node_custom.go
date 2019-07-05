package models

//InnerIPInWithoutError :
func (qs NodeQuerySet) InnerIPInWithoutError(innerIP ...string) NodeQuerySet {
	if len(innerIP) == 0 || innerIP[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("inner_ip IN (?)", innerIP))
}

//StatusNotInWithoutError :
func (qs NodeQuerySet) StatusNotInWithoutError(status ...string) NodeQuerySet {
	if len(status) == 0 || status[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("status NOT IN (?)", status))
}

// ClusterIDInWithoutError :
func (qs NodeQuerySet) ClusterIDInWithoutError(clusterID ...string) NodeQuerySet {
	if len(clusterID) == 0 || clusterID[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("cluster_id IN (?)", clusterID))
}

//SetStatusWithEmpty :
func (u NodeUpdater) SetStatusWithEmpty(status string) NodeUpdater {
	if status == "" || status == "null" {
		return u
	}
	u.fields[string(NodeDBSchema.Status)] = status
	return u
}
