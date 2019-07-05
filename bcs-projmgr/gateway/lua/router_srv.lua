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
local service_name = ngx.var.service
if not service_name then
  ngx.log(ngx.ERR, "failed with no service name")
  ngx.exit(503)
  return
end

if service_name == "" then
  ngx.log(ngx.ERR, "failed with empty service name")
  ngx.exit(503)
  return
end

local query_subdomain = config.env .. "." .. service_name .. "." .. config.ns_domain

if not config.ns_ip then
  ngx.log(ngx.ERR, "DNS ip not exist!")
  ngx.exit(503)
  return
end 

local dnsIps = {}
if type(config.ns_ip) == 'table' then
  for i,v in ipairs(config.ns_ip) do
    table.insert(dnsIps,{v, config.ns_port})
  end
else
  table.insert(dnsIps,{config.ns_ip, config.ns_port})
end


local dns, err = resolver:new{
  nameservers = dnsIps,
  retrans = 2,
  timeout = 250
}

if not dns then
  ngx.log(ngx.ERR, "failed to instantiate the resolver: ", err)
  ngx.exit(503)
  return
end



local records, err = dns:query(query_subdomain, {qtype = dns.TYPE_SRV})

if not records then
  ngx.log(ngx.ERR, "failed to query the DNS server: ", err)
  ngx.exit(503)
  return
end



if records.errcode then
  if records.errcode == 3 then
    ngx.log(ngx.ERR, "DNS error code #" .. records.errcode .. ": ", records.errstr)
    ngx.exit(503)
    return
  else
    ngx.log(ngx.ERR, "DNS error #" .. records.errcode .. ": ", err)
    ngx.exit(503)
    return
  end
end

local host_num = table.getn(records)
local host_index = math.random(host_num)
if records[host_index].port then
  local target_ip = dns:query(records[host_index].target)[1].address
  ngx.var.target = target_ip .. ":" .. records[host_index].port
else
  ngx.log(ngx.ERR, "DNS answer didn't include a port")
  ngx.exit(503)
end
