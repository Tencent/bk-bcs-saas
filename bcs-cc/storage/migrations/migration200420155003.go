package migrations

import (
	"time"

	"github.com/jinzhu/gorm"
)

// HandleMigrate200420155003 :
func (c *MigrationCommand) HandleMigrate200420155003(db *gorm.DB) error {
	type Model struct {
		ID        uint `gorm:"primary_key"`
		CreatedAt time.Time
		UpdatedAt time.Time
		DeletedAt *time.Time
		Extra     string `json:"extra" sql:"type:text"`
	}
	type Cluster struct {
		Model
		Name              string     `json:"name" gorm:"size:64;unique_index:uix_project_id_name"`
		Creator           string     `json:"creator" gorm:"size:32"`
		Description       string     `json:"description" sql:"size:128"`
		ProjectID         string     `json:"project_id" gorm:"size:32;index;unique_index:uix_project_id_name"`
		RelatedProjects   string     `json:"related_projects" sql:"type:text"`
		ClusterID         string     `json:"cluster_id" gorm:"size:64;unique_index"`
		ClusterNum        int64      `json:"cluster_num" gorm:"unique"`
		Status            string     `json:"status" gorm:"size:64"`
		Disabled          bool       `json:"disabled"`
		Type              string     `json:"type" gorm:"size:8"`
		Environment       string     `json:"environment" gorm:"size:8"`
		AreaID            int        `json:"area_id"`
		ConfigSvrCount    int        `json:"config_svr_count"`
		MasterCount       int        `json:"master_count"`
		NodeCount         int        `json:"node_count"`
		IPResourceTotal   int        `json:"ip_resource_total"`
		IPResourceUsed    int        `json:"ip_resource_used"`
		Artifactory       string     `json:"artifactory" gorm:"size:256"`
		TotalMem          float64    `json:"total_mem"`
		RemainMem         float64    `json:"remain_mem"`
		TotalCPU          float64    `json:"total_cpu"`
		RemainCPU         float64    `json:"remain_cpu"`
		TotalDisk         float64    `json:"total_disk"`
		RemainDisk        float64    `json:"remain_disk"`
		CapacityUpdatedAt *time.Time `json:"capacity_updated_at"`
		NotNeedNAT        bool       `json:"not_need_nat" gorm:"default:false"`
		ExtraClusterID    string     `json:"extra_cluster_id" gorm:"size:64"`
		Source            string     `json:"source" gorm:"size:16;default:'bcs_platform'"`
	}

	return db.AutoMigrate(&Cluster{}).Error
}

// HandleRollback200420155003 : rollback handler for HandleMigrate200420155003
func (c *MigrationCommand) HandleRollback200420155003(db *gorm.DB) error {
	return nil
}
