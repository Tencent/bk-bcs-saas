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

package utils

import (
	"github.com/gin-gonic/gin"
)

// Pagination : paginate the data
type Pagination struct {
	Limit  int `form:"limit"`
	Offset int `form:"offset"`
}

// SetDefault : set the default value
func (p *Pagination) SetDefault() {
	if p.Limit == 0 {
		p.Limit = 20
	}
}

// GetPaginationFromContext : get the pagination from context
func GetPaginationFromContext(c *gin.Context, pagination *Pagination) (err error) {
	err = c.Bind(pagination)
	pagination.SetDefault()
	return
}
