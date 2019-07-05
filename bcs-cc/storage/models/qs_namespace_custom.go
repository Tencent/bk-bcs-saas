package models

import "github.com/jinzhu/gorm"

//ClusterIDEqWithEmpty :
func (qs KubernetesNamespaceQuerySet) ClusterIDEqWithEmpty(clusterID string) KubernetesNamespaceQuerySet {
	if clusterID == "" || clusterID == "null" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("cluster_id = ?", clusterID))
}

// ProjectIDInWithoutError : when length of project id is 0, return qs all
func (qs KubernetesNamespaceQuerySet) ProjectIDInWithoutError(projectIDList ...string) KubernetesNamespaceQuerySet {
	if len(projectIDList) == 0 || projectIDList[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("project_id IN (?)", projectIDList))
}

// ClusterIDEqWithEmpty :
func (qs NamespaceQuerySet) ClusterIDEqWithEmpty(clusterID string) NamespaceQuerySet {
	if clusterID == "" || clusterID == "null" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("cluster_id = ?", clusterID))
}

// ProjectIDInWithoutError : when length of project id is 0, return qs all
func (qs NamespaceQuerySet) ProjectIDInWithoutError(projectIDList ...string) NamespaceQuerySet {
	if len(projectIDList) == 0 || projectIDList[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("project_id IN (?)", projectIDList))
}

// DeleteUnscoped : delete a k8s record
func (qs KubernetesNamespaceQuerySet) DeleteUnscoped() error {
	return qs.db.Unscoped().Delete(KubernetesNamespace{}).Error
}

// DeleteUnscoped : delete a k8s record
func (o *KubernetesNamespace) DeleteUnscoped(db *gorm.DB) error {
	return db.Unscoped().Delete(o).Error
}

// DeleteUnscoped : delete a mesos record
func (qs NamespaceQuerySet) DeleteUnscoped() error {
	return qs.db.Unscoped().Delete(Namespace{}).Error
}

// DeleteUnscoped : delete a mesos record
func (o *Namespace) DeleteUnscoped(db *gorm.DB) error {
	return db.Unscoped().Delete(o).Error
}

// SetNameWithEmpty :
func (u KubernetesNamespaceUpdater) SetNameWithEmpty(name string) KubernetesNamespaceUpdater {
	if name == "" {
		return u
	}
	u.fields[string(KubernetesNamespaceDBSchema.Name)] = name
	return u
}

// SetStatusWithEmpty :
func (u KubernetesNamespaceUpdater) SetStatusWithEmpty(status string) KubernetesNamespaceUpdater {
	if status == "" {
		return u
	}
	u.fields[string(KubernetesNamespaceDBSchema.Status)] = status
	return u
}

// SetEnvTypeWithEmpty :
func (u KubernetesNamespaceUpdater) SetEnvTypeWithEmpty(envType string) KubernetesNamespaceUpdater {
	if envType == "" {
		return u
	}
	u.fields[string(KubernetesNamespaceDBSchema.EnvType)] = envType
	return u
}

// SetNameWithEmpty :
func (u NamespaceUpdater) SetNameWithEmpty(name string) NamespaceUpdater {
	if name == "" {
		return u
	}
	u.fields[string(NamespaceDBSchema.Name)] = name
	return u
}

// SetStatusWithEmpty :
func (u NamespaceUpdater) SetStatusWithEmpty(status string) NamespaceUpdater {
	if status == "" {
		return u
	}
	u.fields[string(NamespaceDBSchema.Status)] = status
	return u
}

// SetEnvTypeWithEmpty :
func (u NamespaceUpdater) SetEnvTypeWithEmpty(envType string) NamespaceUpdater {
	if envType == "" {
		return u
	}
	u.fields[string(NamespaceDBSchema.EnvType)] = envType
	return u
}
