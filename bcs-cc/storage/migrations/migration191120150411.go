package migrations

import (
	"time"

	"github.com/jinzhu/gorm"
)

// HandleMigrate191120150411 :
func (c *MigrationCommand) HandleMigrate191120150411(db *gorm.DB) error {
	type Model struct {
		ID        uint `gorm:"primary_key"`
		CreatedAt time.Time
		UpdatedAt time.Time
		DeletedAt *time.Time
		Extra     string `json:"extra" sql:"type:text"`
	}
	type Area struct {
		Model
		Name          string `json:"name" gorm:"size:64;unique_index"`
		Description   string `json:"description" sql:"size:128"`
		Configuration string `json:"configuration" sql:"type:text"`
		ChineseName   string `json:"chinese_name" gorm:"size:64"`
		Source        string `json:"source" gorm:"size:32;default:'BCS'"`
	}
	return db.AutoMigrate(&Area{}).Error
}

// HandleRollback191120150411 : rollback handler for HandleMigrate191120150411
func (c *MigrationCommand) HandleRollback191120150411(db *gorm.DB) error {
	return nil
}
