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

package migrations

import (
	"flag"
	"fmt"
	"reflect"
	"sort"
	"strings"
	"time"

	"bcs_cc/storage"

	"github.com/jinzhu/gorm"
	gormigrate "gopkg.in/gormigrate.v1"
)

type migrationCMP []*gormigrate.Migration

func (m migrationCMP) Len() int      { return len(m) }
func (m migrationCMP) Swap(i, j int) { m[i], m[j] = m[j], m[i] }
func (m migrationCMP) Less(i, j int) bool {
	var (
		err    error
		layout = "060102150405"
	)
	time1, err := time.Parse(layout, m[i].ID)
	if err != nil {
		panic(err)
	}
	time2, err := time.Parse(layout, m[j].ID)
	if err != nil {
		panic(err)
	}
	return time1.Before(time2)
}

// MigrationCommand : migrate command
type MigrationCommand struct {
	Command   string
	Options   *gormigrate.Options
	DBSession *storage.DBSession
}

// ParseFlag :
func (c *MigrationCommand) ParseFlag() (string, error) {
	flag.StringVar(&c.Command, "a", "migrate", "Action to execute(migrate/rollback/list)")

	return "Update database schema", nil
}

func (c *MigrationCommand) getMigrationHandler() *gormigrate.Gormigrate {
	var (
		dbsession  = c.DBSession
		migrations = c.GetMigrations()
		handler    = gormigrate.New(
			dbsession.DB, c.Options, migrations,
		)
	)

	dbsession.DB.LogMode(true)
	return handler
}

func (c *MigrationCommand) migrateCommand() error {
	var handler = c.getMigrationHandler()

	err := handler.Migrate()
	if err != nil {
		panic(err)
	}
	return nil
}

func (c *MigrationCommand) rollbackCommand() error {
	var handler = c.getMigrationHandler()

	err := handler.RollbackLast()
	if err != nil {
		panic(err)
	}
	return nil
}

func (c *MigrationCommand) listCommand() error {
	var (
		migrations = c.GetMigrations()
		count      int
		flag       string
	)
	c.DBSession.DB.LogMode(false)
	for i := range migrations {
		migration := migrations[i]
		c.DBSession.DB.Table(
			c.Options.TableName,
		).Where(
			fmt.Sprintf("%s = ?", c.Options.IDColumnName), migration.ID,
		).Count(&count)
		if count > 0 {
			flag = "*"
		} else {
			flag = " "
		}
		fmt.Printf(" [%s] %s\n", flag, migration.ID)
	}
	return nil
}

// Start :
func (c *MigrationCommand) Start() error {
	c.Options = gormigrate.DefaultOptions
	c.DBSession = storage.GetDefaultSession()
	defer c.DBSession.Close()

	fmt.Printf("Action %v\n", c.Command)
	switch c.Command {
	case "migrate":
		return c.migrateCommand()
	case "rollback":
		return c.rollbackCommand()
	case "list":
		return c.listCommand()
	default:
		return c.listCommand()
	}
}

// GetMigrationByReflectMethod :
func (c *MigrationCommand) GetMigrationByReflectMethod(
	ID string, migrateMethod reflect.Value, rollbackMethod reflect.Value,
) *gormigrate.Migration {
	return &gormigrate.Migration{
		ID: ID,
		Migrate: func(db *gorm.DB) error {
			result := migrateMethod.Call([]reflect.Value{reflect.ValueOf(db)})
			value := result[0].Interface()
			if value == nil {
				return nil
			}
			return value.(error)
		},
		Rollback: func(db *gorm.DB) error {
			result := rollbackMethod.Call([]reflect.Value{reflect.ValueOf(db)})
			value := result[0].Interface()
			if value == nil {
				return nil
			}
			return value.(error)
		},
	}
}

// GetMigrations : get method by prefix
func (c *MigrationCommand) GetMigrations() []*gormigrate.Migration {
	var (
		rtype                 = reflect.TypeOf(c)
		rvalue                = reflect.ValueOf(c)
		number                = rvalue.NumMethod()
		methods               []*gormigrate.Migration
		migrateID             string
		rmethod               reflect.Method
		migrateMethod         reflect.Value
		rollbackMethod        reflect.Value
		migrateMethodPrefix   = "HandleMigrate"
		rollbackMethodPrefix  = "HandleRollback"
		defaultRollbackMethod = rvalue.MethodByName("DefaultRollbackMethod")
	)

	for i := 0; i < number; i++ {
		rmethod = rtype.Method(i)
		if !strings.HasPrefix(rmethod.Name, migrateMethodPrefix) {
			continue
		}
		migrateID = strings.TrimPrefix(rmethod.Name, migrateMethodPrefix)
		migrateMethod = rvalue.Method(rmethod.Index)
		rmethod, ok := rtype.MethodByName(fmt.Sprintf(
			"%s%s", rollbackMethodPrefix, migrateID,
		))
		if ok {
			rollbackMethod = rvalue.Method(rmethod.Index)
		} else {
			rollbackMethod = defaultRollbackMethod
		}
		methods = append(methods, c.GetMigrationByReflectMethod(
			migrateID, migrateMethod, rollbackMethod,
		))
	}
	sort.Sort(migrationCMP(methods))
	return methods
}

// DefaultMigrateMethod : default migrate method
func (c *MigrationCommand) DefaultMigrateMethod() error {
	return nil
}

// DefaultRollbackMethod : default rollback method
func (c *MigrationCommand) DefaultRollbackMethod() error {
	return nil
}
