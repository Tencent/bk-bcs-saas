spring:
  application:
    name: project
    desc: Devops Project Service
    version: 4.0
    packageName: com.tencent.devops.project
  datasource:
    url: jdbc:mysql://__MYSQL_IP__:__MYSQL_PORT__/devops_project?useSSL=false&autoReconnect=true&timezone=+800&useUnicode=true&characterEncoding=utf8&allowMultiQueries=true
    username: __MYSQL_USER__
    password: __MYSQL_PASS__
  cloud:
    consul:
      host: __CONSUL_AGENT_IP__
      port: __CONSUL_AGENT_PORT__
      discovery:
        tags: dev

server:
  port: __DEVOPS_PM_PORT__

#蓝鲸登录平台API地址
bk_login:
  path: http://__PAAS_HOST__/api/c/compapi/v2/bk_login/
  getUser: get_user/
  getAllUser: get_all_users/
  bk_app_code: bkdevops
  bk_app_secret: bkdevops
  #内部企业版蓝鲸平台
  url: http://__PAAS_HOST__
  outurl: __HTTP_SCHEMA__://__PAAS_FQDN__

auth:
  url: http://__IAM_HOST__
  xBkAppCode: __APP_CODE__
  xBkAppSecret: __APP_TOKEN__
bcs_cc:
  externalUrl: http://__BCS_CC_IP__:__BCS_CC_PORT__/project
