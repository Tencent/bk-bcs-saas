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
local http_origin = ngx.var.http_origin

if not http_origin then
  return
end

if http_origin == "" then
  return
end

local allow_hosts = config.allow_hosts

local matched = false
for k, v in pairs(allow_hosts) do
    local from, to, err = ngx.re.find(http_origin, v, "jo")
    if from then
        matched = true
    end
end

if matched == false then
  ngx.log(ngx.ERR, "can not allow access: ", http_origin)
  return
end

local m = ngx.req.get_method()

if m == "OPTIONS" then
  ngx.header["Access-Control-Allow-Origin"] = http_origin
  ngx.header["Access-Control-Allow-Credentials"] = "true"
  ngx.header["Access-Control-Max-Age"] = "1728000"
  ngx.header["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
  ngx.header["Access-Control-Allow-Headers"] = "Authorization,Content-Type,Accept,Origin,User-Agent,Cache-Control,Keep-Alive,X-Requested-With,If-Modified-Since,X-CSRFToken,X-DEVOPS-PROJECT-ID"
  ngx.header["Content-Length"] = "0"
  ngx.header["Content-Type"] = "text/plain charset=UTF-8"
  ngx.exit(204)
end

ngx.header["Access-Control-Allow-Origin"] = http_origin
ngx.header["Access-Control-Allow-Credentials"] = "true"