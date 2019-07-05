#!/bin/bash

export SVR_CONSUL_IP=`getent hosts svr-consul | awk '{ print $1 }'`

export DEVOPS_HOST=`echo $DEV_DEVOPS_HOST | awk -F"/" '{print $3}'`
export DEVOPS_API_FQDN=`echo $DEV_DEVOPS_API_HOST | awk -F"/" '{print $3}'`
export BCS_APP_FQDN=`echo $DEV_BCS_APP_HOST | awk -F"/" '{print $3}'`
export PAAS_FQDN=`echo $BK_PAAS_HOST | awk -F"/" '{print $3}'`

# nginx 配置
cd /usr/local/openresty/nginx/conf || exit 1

# # 配置 frontend.conf
cp -rf frontend.conf.tpl frontend.conf
sed -i "s/__DEVOPS_HOST__/$DEVOPS_HOST/g" frontend.conf

# 配置 backend.conf
cp -rf backend.conf.tpl backend.conf
sed -i "s/__DEVOPS_API_FQDN__/$DEVOPS_API_FQDN/g" backend.conf

# 配置 init.lua
cd lua || exit 1
cp -rf init.lua.dev-tpl init.lua
sed -i "s/__SVR_CONSUL_IP__/$SVR_CONSUL_IP/g" init.lua

# 前端配置
cd /usr/local/openresty/nginx

cp -rf frontend/console/static/env.js.tpl frontend/console/static/env.js
sed -i "s/__PAAS_FQDN__/$PAAS_FQDN/g" frontend/console/static/env.js
sed -i "s/__DEVOPS_API_FQDN__/$DEVOPS_API_FQDN/g" frontend/console/static/env.js
sed -i "s/__BCS_APP_FQDN__/$BCS_APP_FQDN/g" frontend/console/static/env.js

mkdir -p run
openresty -g "daemon off;"