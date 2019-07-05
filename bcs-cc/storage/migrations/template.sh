#!/bin/sh

MID=`date +%y%m%d%k%M%S`

cat > $1/migration${MID}.go << EOF
package migrations

import (
	"github.com/jinzhu/gorm"
)

// HandleMigrate${MID} : 
func (c *MigrationCommand) HandleMigrate${MID}(db *gorm.DB) error {
	DoMigrate Here

	return nil
}

// HandleRollback${MID} : rollback handler for HandleMigrate${MID}
func (c *MigrationCommand) HandleRollback${MID}(db *gorm.DB) error {
	return nil
}
EOF