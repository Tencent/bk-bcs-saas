package models

import (
	"bcs_cc/utils"
	"fmt"

	"github.com/jinzhu/gorm"
)

// ProjectIDInWithoutError : when length of project id is 0, return qs all
func (qs ProjectQuerySet) ProjectIDInWithoutError(projectIDList ...string) ProjectQuerySet {
	if len(projectIDList) == 0 || projectIDList[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("project_id IN (?)", projectIDList))
}

// EnglishNameInWithoutError : when length of english name is 0, return qs all
func (qs ProjectQuerySet) EnglishNameInWithoutError(englishNameList ...string) ProjectQuerySet {
	if len(englishNameList) == 0 || englishNameList[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("english_name IN (?)", englishNameList))
}

type functionType func(ProjectQuerySet, string, string) ProjectQuerySet

// Filter : filter with field
func (qs ProjectQuerySet) Filter(fields map[string]string, f functionType) ProjectQuerySet {
	for field, val := range fields {
		if val == "" {
			continue
		}
		qs = f(qs, field, val)
	}
	return qs
}

// function for query
func filterString(qs ProjectQuerySet, field string, val string) ProjectQuerySet {
	switch field {
	case "creator":
		return qs.CreatorEq(val)
	}
	return qs
}

//
func filterUint(qs ProjectQuerySet, field string, val string) ProjectQuerySet {
	valInt, err := utils.String2Int(val)
	if err != nil {
		qs.db.AddError(fmt.Errorf("%s must be digital", field))
		return qs
	}
	switch field {
	case "approval_status":
		return qs.ApprovalStatusEq(uint(valInt))
	case "project_type":
		return qs.ProjectTypeEq(uint(valInt))
	}
	return qs
}

func filterBool(qs ProjectQuerySet, field string, val string) ProjectQuerySet {
	valBool := !(val == "false")
	switch field {
	case "is_secrecy":
		return qs.IsSecrecyEq(valBool)
	case "is_offline":
		return qs.IsOfflinedEq(valBool)
	}
	return qs
}

// SetNameWithEmpty : update name
func (u ProjectUpdater) SetNameWithEmpty(name string) ProjectUpdater {
	if name == "" {
		return u
	}
	u.fields[string(ProjectDBSchema.Name)] = name
	return u
}

// CustomeUpdate : custome update for many field
func (o *Project) CustomeUpdate(db *gorm.DB, fields ...ProjectDBSchemaField) error {
	dbNameToFieldName := map[string]interface{}{
		"id":              o.ID,
		"created_at":      o.CreatedAt,
		"updated_at":      o.UpdatedAt,
		"deleted_at":      o.DeletedAt,
		"extra":           o.Extra,
		"name":            o.Name,
		"english_name":    o.EnglishName,
		"creator":         o.Creator,
		"updator":         o.Updator,
		"description":     o.Description,
		"project_type":    o.ProjectType,
		"is_offlined":     o.IsOfflined,
		"project_id":      o.ProjectID,
		"use_bk":          o.UseBK,
		"cc_app_id":       o.CCAppID,
		"kind":            o.Kind,
		"deploy_type":     o.DeployType,
		"bg_id":           o.BGID,
		"bg_name":         o.BGName,
		"dept_id":         o.DeptID,
		"dept_name":       o.DeptName,
		"center_id":       o.CenterID,
		"center_name":     o.CenterName,
		"data_id":         o.DataID,
		"is_secrecy":      o.IsSecrecy,
		"approval_status": o.ApprovalStatus,
		"logo_addr":       o.LogoAddr,
		"approver":        o.Approver,
		"remark":          o.Remark,
		"approval_time":   o.ApprovalTime,
	}
	notEmptyFields := []string{"name", "log_addr"}
	u := map[string]interface{}{}
	for _, f := range fields {
		fs := f.String()
		if utils.StringInSlice(fs, notEmptyFields) && dbNameToFieldName[fs] == "" {
			continue
		}
		u[fs] = dbNameToFieldName[fs]
	}
	if err := db.Model(o).Updates(u).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return err
		}

		return fmt.Errorf("can't update Project %v fields %v: %s",
			o, fields, err)
	}

	return nil
}

// ProjectNameInWithoutError : get project info by project names, not raise error
func (qs ProjectQuerySet) ProjectNameInWithoutError(projectNameList ...string) ProjectQuerySet {
	if len(projectNameList) == 0 || projectNameList[0] == "" {
		return qs.w(qs.db)
	}
	return qs.w(qs.db.Where("name IN (?)", projectNameList))
}
