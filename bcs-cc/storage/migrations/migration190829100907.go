package migrations

import (
	"time"

	"github.com/jinzhu/gorm"
)

// HandleMigrate190829100907 :
func (c *MigrationCommand) HandleMigrate190829100907(db *gorm.DB) error {
	type Model struct {
		ID        uint `gorm:"primary_key"`
		CreatedAt time.Time
		UpdatedAt time.Time
		DeletedAt *time.Time
		Extra     string `json:"extra" sql:"type:text"`
	}
	type Namespace struct {
		Model
		Name           string `json:"name" gorm:"size:63;unique_index:idx_name_code"`
		Creator        string `json:"creator" gorm:"size:31"`
		Description    string `json:"description" sql:"size:127"`
		ProjectID      string `json:"project_id" gorm:"size:32;index"`
		ClusterID      string `json:"cluster_id" gorm:"size:32;index;unique_index:idx_name_code"`
		EnvType        string `json:"env_type" gorm:"size:16"`
		Status         string `json:"status" gorm:"size:16"`
		HasImageSecret bool   `json:"has_image_secret" gorm:"default:false"` // 是否有secret
	}
	// delele previous restricted index
	if err := db.Model(&Namespace{}).RemoveIndex("uix_namespace_name").Error; err != nil {
		return err
	}
	if err := db.Model(&Namespace{}).RemoveIndex("uix_namespaces_name").Error; err != nil {
		return err
	}
	return db.AutoMigrate(&Namespace{}).Error
}

// HandleRollback190829100907 : rollback handler for HandleMigrate190829100907
func (c *MigrationCommand) HandleRollback190829100907(db *gorm.DB) error {
	return nil
}
