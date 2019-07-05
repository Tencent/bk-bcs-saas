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

package tests

import (
	"bcs_cc/confcenter/apis"
	"bcs_cc/utils"
	"testing"

	"github.com/stretchr/testify/suite"
)

type ProjectTypeTestSuite struct {
	suite.Suite
	InfoStringSlice []string
	InfoBoolSlice   []bool
}

func (suite *ProjectTypeTestSuite) SetupTest() {
	suite.InfoStringSlice = []string{"test:123", "test1:123"}
	suite.InfoBoolSlice = []bool{false, true}
}

func (suite *ProjectTypeTestSuite) TestProjectStringFromInterface() {
	data, _ := apis.GetPojectFromAuthData(suite.InfoStringSlice)
	suite.Equal(2, len(data))
}

func (suite *ProjectTypeTestSuite) TestProjectBoolFromInterface() {
	data, _ := apis.GetPojectFromAuthData(suite.InfoBoolSlice)
	suite.Equal(0, len(data))
}

func TestProjectTypeTestSuite(t *testing.T) {
	suite.Run(t, new(ProjectTypeTestSuite))
}

// test StringInSlice
type StringInSliceTestSuite struct {
	suite.Suite
	stringItem     string
	failStringItem string
	stringSlice    []string
}

func (suite *StringInSliceTestSuite) SetupTest() {
	suite.stringItem = "test"
	suite.failStringItem = "test2"
	suite.stringSlice = []string{"test", "test1"}
}

func (suite *StringInSliceTestSuite) TestSuccessInSlice() {
	suite.Equal(true, utils.StringInSlice(suite.stringItem, suite.stringSlice))
}

func (suite *StringInSliceTestSuite) TestFailInSlice() {
	suite.Equal(false, utils.StringInSlice(suite.failStringItem, suite.stringSlice))
}

func TestStringInSliceTestSuite(t *testing.T) {
	suite.Run(t, new(StringInSliceTestSuite))
}

type Camel2SnakeTestSuite struct {
	suite.Suite
	TestString string
}

func (suite *Camel2SnakeTestSuite) SetupTest() {
	suite.TestString = "thisIsATestID"
}

func (suite *Camel2SnakeTestSuite) TestSuccess() {
	suite.Equal("this_is_a_test_id", utils.Camel2Snake(suite.TestString))
}

func TestCamel2SnakeTestSuite(t *testing.T) {
	suite.Run(t, new(Camel2SnakeTestSuite))
}

type RandSelectorTestSuite struct {
	suite.Suite
	TestSlice []interface{}
}

func (suite *RandSelectorTestSuite) SetupTest() {
	suite.TestSlice = []interface{}{"t1", "t2", "t3", "t4"}
}

func (suite *RandSelectorTestSuite) TestRandSelector() {
	temp := utils.RandSelector(&suite.TestSlice)
	suite.NotNil(temp)
}

func TestRandSelectorTestSuite(t *testing.T) {
	suite.Run(t, new(RandSelectorTestSuite))
}
