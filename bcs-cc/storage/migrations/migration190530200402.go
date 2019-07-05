package migrations

import (
	"time"

	"github.com/jinzhu/gorm"
)

// HandleMigrate190530200402 :
func (c *MigrationCommand) HandleMigrate190530200402(db *gorm.DB) error {
	type Model struct {
		ID        uint `gorm:"primary_key"`
		CreatedAt time.Time
		UpdatedAt time.Time
		DeletedAt *time.Time
		Extra     string `json:"extra" sql:"type:text"`
	}

	type Project struct {
		Model
		Name           string    `json:"name" gorm:"size:64;unique"`
		EnglishName    string    `json:"english_name" gorm:"size:64;unique;index"`
		Creator        string    `json:"creator" gorm:"size:32"`
		Updator        string    `json:"updator" gorm:"size:32"`
		Description    string    `json:"desc" sql:"type:text"`
		ProjectType    uint      `json:"project_type"`
		IsOfflined     bool      `json:"is_offlined" gorm:"default:false"`
		ProjectID      string    `json:"project_id" gorm:"size:32;unique;index"`
		UseBK          bool      `json:"use_bk" gorm:"default:false"`
		CCAppID        uint      `json:"cc_app_id"`
		Kind           uint      `json:"kind"`
		DeployType     string    `json:"deploy_type"`
		BGID           uint      `json:"bg_id"`
		BGName         string    `json:"bg_name"`
		DeptID         uint      `json:"dept_id"`
		DeptName       string    `json:"dept_name"`
		CenterID       uint      `json:"center_id"`
		CenterName     string    `json:"center_name"`
		DataID         uint      `json:"data_id"`
		IsSecrecy      bool      `json:"is_secrecy" gorm:"default:false"`
		ApprovalStatus uint      `json:"approval_status" gorm:"default:2"`
		LogoAddr       string    `json:"logo_addr" sql:"type:text"`
		Approver       string    `json:"approver" gorm:"size:32"`
		Remark         string    `json:"remark" sql:"type:text"`
		ApprovalTime   time.Time `json:"approval_time"`
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
	}
	type BaseVersion struct {
		Model
		Creator     string `json:"creator" gorm:"size:32"`
		Kind        string `json:"kind" gorm:"size:16;default:'k8s';unique_index:uix_version_kind_environment"`
		Version     string `json:"version" gorm:"size:64";unique_index:uix_version_kind_environment`
		SubVersion  string `json:"sub_version" gorm:"size:64"`
		Environment string `json:"environment" gorm:"size:64;default:'prod'";unique_index:uix_version_kind_environment`
		Configure   string `json:"configure" sql:"type:text"`
	}
	type ClusterConfigureVersion struct {
		Model
		Creator   string `json:"creator" gorm:"size:32"`
		ClusterID string `json:"cluster_id" gorm:"size:64"`
		Snapshot  string `json:"snapshot" sql:"type:text"`
	}
	type ClusterHistoryData struct {
		ID                uint      `gorm:"primary_key"`
		CreatedAt         time.Time `json:"created_at"`
		ProjectID         string    `json:"project_id" gorm:"size:32;index"`
		ClusterID         string    `json:"cluster_id" gorm:"size:64;index"`
		Environment       string    `json:"environment" gorm:"size:8"` // stag,debug,prod
		TotalMem          float64   `json:"total_mem"`
		RemainMem         float64   `json:"remain_mem"`
		TotalCPU          float64   `json:"total_cpu"`
		RemainCPU         float64   `json:"remain_cpu"`
		TotalDisk         float64   `json:"total_disk"`
		RemainDisk        float64   `json:"remain_disk"`
		CapacityUpdatedAt time.Time `json:"capacity_updated_at" gorm:"index"`
	}
	type ManagerMaster struct {
		Model
		InnerIP      string `json:"inner_ip" gorm:"size:64;unique_index"`
		ClusterID    string `json:"cluster_id" gorm:"size:128"`
		ProjectID    string `json:"project_id" gorm:"size:32"`
		ExtendedInfo string `json:"extended_info" sql:"type:text"`
		Num          int    `json:"num"`
		Backup       string `json:"backup" gorm:"size:128"`
		Hostname     string `json:"hostname" gorm:"size:128"`
		Status       string `json:"status" gorm:"size:16"`
	}
	type Node struct {
		Model
		Name        string  `json:"name" gorm:"size:63"`
		Creator     string  `json:"creator" gorm:"size:31"`
		Description string  `json:"description" sql:"size:127"`
		ProjectID   string  `json:"project_id" gorm:"size:32;index"`
		ClusterID   string  `json:"cluster_id" gorm:"size:32;index"`
		Status      string  `json:"status" gorm:"size:16"`
		Kind        string  `json:"kind" gorm:"size:16"`
		InnerIP     string  `json:"inner_ip" gorm:"size:64;unique_index"`
		OutterIP    string  `json:"outter_ip" gorm:"size:255"`
		DeviceClass string  `json:"device_class" gorm:"text"`
		CPU         float64 `json:"cpu" gorm:"default:0"`
		MEM         float64 `json:"mem" gorm:"default:0"`
		Disk        float64 `json:"disk" gorm:"default:0"`
		IPResources float64 `json:"ip_resources" gorm:"default:0"`
	}

	type Namespace struct {
		Model
		Name           string `json:"name" gorm:"size:63;unique_index"`
		Creator        string `json:"creator" gorm:"size:31"`
		Description    string `json:"description" sql:"size:127"`
		ProjectID      string `json:"project_id" gorm:"size:32;index"`
		ClusterID      string `json:"cluster_id" gorm:"size:32;index"`
		EnvType        string `json:"env_type" gorm:"size:16"`
		Status         string `json:"status" gorm:"size:16"`
		HasImageSecret bool   `json:"has_image_secret" gorm:"default:false"`
	}
	type KubernetesNamespace struct {
		Model
		Name           string `json:"name" gorm:"size:63;unique_index:idx_name_code"`
		Creator        string `json:"creator" gorm:"size:31"`
		Description    string `json:"description" sql:"size:127"`
		ProjectID      string `json:"project_id" gorm:"size:32"`
		ClusterID      string `json:"cluster_id" gorm:"size:32;unique_index:idx_name_code"`
		EnvType        string `json:"env_type" gorm:"size:16"`
		Status         string `json:"status" gorm:"size:16"`
		HasImageSecret bool   `json:"has_image_secret" gorm:"default:false"`
	}
	type Area struct {
		Model
		Name          string `json:"name" gorm:"size:64;unique_index"`
		Description   string `json:"description" sql:"size:128"`
		Configuration string `json:"configuration" sql:"type:text"`
		ChineseName   string `json:"chinese_name" gorm:"size:64"`
	}
	type FunctionControl struct {
		Model
		FuncCode    string `json:"func_code" gorm:"size:64;unique"`
		Description string `json:"description" gorm:"size:100"`
		FuncStatus  bool   `json:"func_status" gorm:"default:false"`
		WhiteList   string `json:"white_list" sql:"type:text"`
		Creator     string `json:"creator" gorm:"size:32"`
		Updator     string `json:"updator" gorm:"size:32"`
	}
	type ZookeeperConfig struct {
		Model
		Name         string `json:"name" gorm:"size:32"`
		Desc         string `json:"desc" sql:"type:text"`
		Zookeeper    string `json:"zookeeper" sql:"type:text"`
		BCSZookeeper string `json:"bcs_zookeeper" sql:"type:text"`
		Environment  string `json:"environment" gorm:"size:8;unique_index"`
		Creator      string `json:"creator" gorm:"size:16"`
		Updator      string `json:"updator" gorm:"size:16"`
		Kind         uint8  `json:"kind" gorm:"default:2"`
	}
	type ManagerModule struct {
		Model
		InnerIP    string `json:"inner_ip" gorm:"size:64"`
		ModuleName string `json:"module_name" gorm:"size:64"`
		ClusterID  string `json:"cluster_id" gorm:"size:127"`
		ProjectID  string `json:"project_id" gorm:"size:32;index"`
		Port       int    `json:"port"`
		Path       string `json:"path" gorm:"size:128"`
		Version    string `json:"version" gorm:"size:128"`
		Status     string `json:"status" gorm:"size:128"`
		Backup     string `json:"backup" gorm:"size:256"`
		DeployAt   time.Time
	}
	tableMap := map[string]interface{}{
		"projects":                   &Project{},
		"clusters":                   &Cluster{},
		"base_versions":              &BaseVersion{},
		"cluster_configure_versions": &ClusterConfigureVersion{},
		"cluster_history_data":       &ClusterHistoryData{},
		"manager_masters":            &ManagerMaster{},
		"node":                       &Node{},
		"namespaces":                 &Namespace{},
		"kubernetes_namespaces":      &KubernetesNamespace{},
		"areas":                      &Area{},
		"function_controls":          &FunctionControl{},
		"zookeeper_configs":          &ZookeeperConfig{},
		"manager_modules":            &ManagerModule{},
	}
	for tableName, tableStruct := range tableMap {
		var err error
		if !db.HasTable(tableName) {
			err = db.AutoMigrate(tableStruct).Error
		}
		if err != nil {
			return err
		}
	}
	return nil
}

// HandleRollback190530200402 : rollback handler for HandleRollback190530200402
func (c *MigrationCommand) HandleRollback190530200402(db *gorm.DB) error {
	return nil
}
