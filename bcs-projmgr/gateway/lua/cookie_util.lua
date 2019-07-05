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
_M = {}

function _M:get_cookie(cookie_name)
    
    --- bk用户验证
    local cookie, err = ck:new()
    if not cookie then
        ngx.log(ngx.ERR, "failed to parse user request cookies: ", err)
        -- ngx.exit(401)
        return nil
    end
    
    --- 获取Cookie中bk_ticket
    local cookie_value, err = cookie:get(cookie_name)
    if not cookie_value then
        ngx.log(ngx.ERR, "failed to read user request ", cookie_name, " cookie_value:" , err)
        -- ngx.exit(401)
        return nil
    end
    return cookie_value
end


return _M