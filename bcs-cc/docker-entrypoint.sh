#!/bin/bash

# 配置 dev.yaml
cp -rf /data/etc/dev.yaml.tpl /data/etc/dev.yaml

sed -i "s|__IAM_HOST__|$IAM_HOST|g" /data/etc/dev.yaml
sed -i "s|__HTTP_PROXY__|$HTTP_PROXY|g" /data/etc/dev.yaml
sed -i "s|__APIGW_HOST__|$APIGW_HOST|g" /data/etc/dev.yaml
sed -i "s|__BCS_CC_APP_TOKEN__|$BCS_CC_APP_TOKEN|g" /data/etc/dev.yaml

bcs_cc cc -c /data/etc/dev.yaml