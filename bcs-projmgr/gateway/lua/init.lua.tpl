--[[
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
]]
config = {
  env = "dev",
  static_dir = "__DEVOPS_STAITC_DIR__",
  log_dir = "__DEVOPS_LOGS_DIR__",
  allow_hosts = {
    [==[.*\.__BK_DOMAIN__]==]
  },
  ns_ip = "127.0.0.1",
  ns_port = __DEVOPS_CONSUL_DNSPORT__,
  ns_domain = "service.__DEVOPS_CONSUL_DOMAIN__"
}


string = require("string")
math = require("math")
json = require("cjson.safe")
uuid = require("resty.jit-uuid")
ck = require("resty.cookie")
resolver = require("resty.dns.resolver")
http = require("resty.http")
md5 = require("resty.md5")
cookieUtil = require("cookie_util")

math.randomseed(os.time())
uuid.seed()