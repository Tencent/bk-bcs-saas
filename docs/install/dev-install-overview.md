# 蓝鲸容器管理平台SaaS本地开发部署文档

## 本地环境搭建

在实际的生产环境中，容器管理平台SaaS的部署架构如[拓扑图](/docs/overview/project_deploy.md)所示，依赖蓝鲸体系下其他的产品服务。因此，在搭建本地环境时，建议先完成社区版的[部署]()，再将本地开发环境的相应配置设置成社区版的服务配置(复用社区版的其他产品服务)，以便快速在本地进行开发联调。

### 普通方式

bcs-projmgr、bcs-app、bcs-cc三者启动顺序并没有强依赖性，推荐按bcs-cc=>bcs-app=>bcs-projmgr顺序进行部署
- [安装部署bcs-cc](./dev-install-bcs-cc.md)
- [安装部署bcs-app](./dev-install-bcs-app.md)
- [安装部署bcs-projmgr](./dev-install-bcs-projmgr.md)

### 容器化方式[推荐]

对于开发和测试环境，我们建议通过运行Docker容器来安装容器管理平台SaaS。采用[Docker Compose](https://docs.docker.com/compose/overview/)，你可以在单个主机上，快速完成SaaS中3个模块的部署工作

##### 1. 配置变量 & host
复制 .env.tpl 为 .env, 按指引修改环境变量。下面是示例配置:
```
# 全局配置
BK_PAAS_HOST=http://paas.bk.com                            # 社区版PaaS地址
IAM_HOST=http://iam.service.consul                         # 社区版权限中心后台地址
APIGW_HOST=http://paas.service.consul                      # 社区版APIGW地址

# 本地开发域名，配置成127.0.0.1
# 二级域名需要和社区版PaaS一致(如bk.com)
DEV_DEVOPS_HOST=http://dev.devops.bk.com                   # 容器管理平台SaaS首页
DEV_DEVOPS_API_HOST=http://api.dev.devops.bk.com           # bcs-projmgr后台api地址
DEV_BCS_APP_HOST=http://dev.paas.bk.com:8000               # bcs-app地址

# bcs-app 配置
BCS_APP_APP_TOKEN=                                         # bcs-app token
ARTIFACTORY_HOST=hub.bk.com:80                             # 社区版Habor地址
THANOS_HOST=http://query.thanos.service.consul:19192       # 社区版Thanos地址
HARBOR_CHARTS_HOST=http://hub.bk.com                       # 社区版Habor地址(用于Helm Charts Repo)
BCS_API_HOST=api.bcs.service.consul                        # 社区版bcs-services地址

# 社区版中控机执行命令获取 
BCS_CC_APP_TOKEN=                                          # bcs-cc token

# 社区版中控机执行命令获取
BCS_PM_APP_TOKEN=                                          # bcs-projmgr token

# 代理配置[可选]
# bcs-projmgr pm模块使用
PROXY_HOST=
PROXY_PORT=
NON_PROXY_HOSTS=svr-consul|bcs-cc

# 环境变量[可选]
HTTP_PROXY=
HTTPS_PROXY=
NO_PROXY=svr-consul,bcs-cc
```

注意: 
- docker-compose `.env` 配置`不需要加单双引号`(它们会作为变量的一部分)，参考[Docker Compose官方文档](https://docs.docker.com/compose/env-file/)
- *.service.consul如果本地无法ping通，需要去社区版查出实际ip(可在中控机ping域名得出ip)，并配置到本地hosts中，或者直接添加到docker-compose.yml中，示例如下

```yaml
x-bcs-common:
  extra_host: &bcs_extra_hosts
    - iam.service.consul:10.0.0.1
    - paas.service.consul:10.0.0.1
```
- 社区版中控机获取token并配置到.env文件中

```bash
# 获取BCS_APP_APP_TOKEN
source /data/install/utils.fc && _app_token bk_bcs_app
# 获取BCS_CC_APP_TOKEN
source /data/install/utils.fc && _app_token bk_bcs
# 获取BCS_PM_APP_TOKEN
source /data/install/utils.fc && _app_token bk_bcs_devops
```

##### 2. 编译前端静态资源

```bash
# 编译前端资源
# 注意: bcs-app/frontend, bcs-projmgr/frontend 源码修改需要重新编译

# 编译 bcs-app/frontend 静态资源
docker run --rm -it -v `pwd`/bcs-app/frontend:/data node:10.15.3-stretch bash -c "cd /data && npm install . && npm run build"

# 编译 bcs-projmgr/frontend 静态资源
docker run --rm -it -v `pwd`/bcs-projmgr/frontend:/data node:10.15.3-stretch bash -c "cd /data && npm install . && npm run public"
```

##### 3. 创建和 Migrate 数据库

```bash
# 启动 mariadb 服务
docker-compose up -d svr-mariadb

# 添加授权, 默认密码为 open-bcs-saas
docker-compose exec svr-mariadb mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'open-bcs-saas' WITH GRANT OPTION;FLUSH PRIVILEGES;"

# 创建&migrate bcs-pm 数据库
docker-compose exec svr-mariadb bash -c "mysql -uroot < /data/bcs-projmgr/support-files/sql/devops_pm.sql"

# 创建 bcs-cc 数据库
docker-compose exec svr-mariadb mysql -uroot -e "create database if not exists \`bcs-cc\` default character set utf8mb4 collate utf8mb4_general_ci;"

# migrate bcs-cc 数据库, dev.yaml.tpl 默认包含了本地数据库账号和密码
docker-compose run --rm bcs-cc bcs_cc migrate -c /data/etc/dev.yaml.tpl

# 初始化 bcs-cc 数据，需要从社区版中控机获取部分配置
bcs-cc/scripts/init_data.sh

# 创建 bcs-app 数据库
docker-compose exec svr-mariadb mysql -uroot -e "create database if not exists \`bcs-app\` default character set utf8mb4 collate utf8mb4_general_ci;"

# migrate bcs-app 数据库
docker-compose run --rm bcs-app python manage.py migrate
```

注意：
- 通过社区版中控机获取区域配置、ZK配置、K8S版本配置、Mesos版本配置并配置到bcs-cc/scripts/init_data.sh文件中

```bash
source /data/install/utils.fc
# 获取区域配置AREA_CONFIG
ssh $BCS_CC_IP 'cat /data/bkce/etc/bcs/cc-area.json' | tr -d '\n'
# 获取zk配置ZK_CONFIG
ssh $BCS_CC_IP 'cat /data/bkce/etc/bcs/cc-zk.json'
# 获取k8s版本K8S_VERSION
echo $K8S_VERSION
# 获取k8s版本配置K8S_CONFIG
ssh $BCS_CC_IP 'cat /data/bkce/etc/bcs/cc-k8s.json' | tr -d '\n'
# 获取mesos版本MESOS_VERSION
echo $MESOS_VERSION
# 获取mesos版本配置MESOS_CONFIG
ssh $BCS_CC_IP 'cat /data/bkce/etc/bcs/cc-mesos.json' | tr -d '\n'
```


##### 4. 打包镜像并启动服务

```bash
# 打包镜像
# 注意: bcs-projmgr/pm，bcs-cc, bcs-app/requirements.txt 源码修改需要重新 build 镜像
docker-compose build

# 启动服务
docker-compose up -d
```

##### 5. 访问服务
访问上面配置的 `DEV_DEVOPS_HOST` ，体验本地环境容器服务

##### 6. 其他快捷操作(非必须)

- reload gateway配置

```bash
docker-compose exec gateway bash -c "cd /usr/local/openresty/nginx && openresty -s reload"
```

## 试一试：初始化集群

集群是容器服务的基础，下面简要介绍如何搭建一个集群。

##### 1. 登录蓝鲸容器服务控制台
登录蓝鲸容器服务控制台，使用你搭建的蓝鲸社区版登录账号即可

##### 2. 创建项目（也可选择已有项目）
- 创建新项目：进入项目管理页面，点击“创建新项目”按钮，完成项目创建操作
- 获取已有项目权限：进入蓝鲸权限中心，申请加入已有项目用户组来获取项目使用权限

##### 3. 创建集群
在容器服务左侧导航中点击“集群”进入集群管理页面，点击“创建集群”按钮

##### 4. 添加集群节点
集群创建成功后，你可以进入集群节点列表，为集群增加节点。创建好集群后，你可以进一步体验模板集等功能，更多使用说明请参考[官方白皮书](https://docs.bk.tencent.com/bcs/)

注意：由于本地环境对接的是社区版的bk-cmdb，因此建议划分特定业务机器给本地联调使用，以免对社区版造成影响