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

package main

import (
	"errors"
	"flag"
	"fmt"
	"os"

	"bcs-cc/confcenter"
	"bcs-cc/config"
	"bcs-cc/logging"
	"bcs-cc/storage/migrations"
)

// CustomCommand : interface of commands
type CustomCommand interface {
	ParseFlag() (string, error)
	Start() error
}

type usageCommand struct {
	Commands map[string]CustomCommand
}

func (c *usageCommand) ParseFlag() (string, error) {
	return "", nil
}

func (c *usageCommand) Start() error {
	c.Usage("", "")
	os.Exit(1)
	return nil
}

func (c *usageCommand) Usage(command string, description string) {
	if command == "" {
		fmt.Printf("支持的命令:\n")
		fmt.Printf("%10s: 启动配置中心主程序\n%10s: 查看配置\n%10s: 数据库migrate\n\n", "cc", "confinfo", "migrate")
	} else {
		fmt.Printf("Command %v: %v\n", command, description)
	}
}

func (c *usageCommand) Handle() (CustomCommand, error) {
	var (
		argv           = len(os.Args)
		command        = ""
		commandArgs    []string
		commandHandler CustomCommand
	)
	if argv > 1 {
		command = os.Args[1]
	}
	if argv > 2 {
		commandArgs = os.Args[2:]
	}

	commandHandler, ok := c.Commands[command]
	if !ok {
		// commandHandler = c
		return c, errors.New("not found command")
	}

	_, err := commandHandler.ParseFlag()
	if err != nil {
		return nil, err
	}

	flag.CommandLine.Parse(commandArgs)

	return commandHandler, nil
}

func getCommandHandler() (CustomCommand, error) {
	var usagecmd = usageCommand{
		Commands: map[string]CustomCommand{
			"cc":       &confcenter.Command{},
			"confinfo": &config.Command{},
			"migrate":  &migrations.MigrationCommand{},
		},
	}
	return usagecmd.Handle()
}

func main() {
	var (
		configPath     string
		err            error
		commandHandler CustomCommand
	)

	flag.StringVar(&configPath, "c", "bcs_cc.yaml", "Configuration yaml path")

	commandHandler, err = getCommandHandler()
	if err != nil {
		commandHandler.Start()
	}
	// read the configure file
	err = config.GlobalConfigurations.ReadFrom(configPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "configuration not found or error, configure path is: %v, error: %v\n", configPath, err)
		return
	}

	err = logging.Init()
	if err != nil {
		panic(err)
	}
	defer logging.Close()

	// start command
	err = commandHandler.Start()
	if err != nil {
		panic(err)
	}
}
