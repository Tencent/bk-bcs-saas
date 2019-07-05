# 容器管理平台项目管理模块（BCS-PROJMGR）安装部署文档

建议先部署[bcs-cc](/docs/install/dev-install-bcs-cc.md)，再部署该模块。

## 系统要求

- 数据库:mysql 5.5
- 名字服务:Consul 1.0及以上
- Java版本:Oracle-JKD1.8.0_161
- Gradle版本:4.8.1
- OpenResty版本:1.11及以上


## 本地开发环境搭建步骤

### 一、Conusl名字服务

#### 1.安装指南

参考Conusl官网推荐的安装方法：[Consul安装指南](https://learn.hashicorp.com/consul/getting-started/install)。下面以MacOS为例子进行说明。

- 下载最新Consul 1.5.1版本[Consul 1.5.1版本](https://releases.hashicorp.com/consul/1.5.1/)。
- 解压consul_1.5.1_darwin_amd64.zip包，可以得到可运行的二进制文件consul。
- 修改consul二进制文件的权限，`chmod 766 consul`。
- 将consul文件复制到系统目录下即可完成安装，`cp ./consul /usr/local/bin/`。

#### 2.启动consul服务

consul进程启动分为2种方式：Client模式、Server模式。

***本地开发启动服务器模式即可***。

- consul server启动(IP:10.10.10.1)

```shell
sudo consul agent -server -data-dir=__CONSUL_DATA_DIR__ -ui -bootstrap -datacenter=__CONSUL_DATACENTER__ -domain=__CONSUL_DOMAIN__ -bootstrap -client=0.0.0.0 -bind=__LOCALHOST_IP__
# 例子：
sudo consul agent -server -data-dir=/data/consul -ui -bootstrap -datacenter=bkdevops -domain=bkdevops -bootstrap -client=0.0.0.0 -bind=10.10.10.1
```

- consul client启动(IP:10.10.10.2)

```shell
sudo consul agent -data-dir=__CONSUL_DATA_DIR__ -datacenter=__CONSUL_DATACENTER__ -domain=__CONSUL_DOMAIN__ -join=__CONSUL_SERVER_IP__ -bind=__LOCALHOST_IP__
# 例子：
sudo consul agent -data-dir=/data/consul -datacenter=enterprise -domain=bkdevops -join=10.10.10.1 -bind=10.10.10.2
```

#### 3.本地开发参数配置说明

| 变量名 | 说明 |
|-------|------|
| __CONSUL_DATA_DIR__ | consul运行数据的目录,默认值"/data/consul" |
| __CONSUL_DATACENTER__ | consul数据中心的名称,默认值"bkdevops"|
| __CONSUL_DOMAIN__ | consul域名的名称,默认值"bkdevops"|
| __LOCALHOST_IP__ |  本地IP地址|
| __CONSUL_SERVER_IP__ | consul server的IP地址|

#### 4.打开consul管理页面

consul启动成功后，可以通过页面来查看相关信息。[Consul管理页面](http://127.0.0.1:8500/ui)

---

### 二、Gateway的安装部署

#### 1.Openresty安装

参考Openresty官网推荐的安装方法：[openresty安装指南](http://openresty.org/cn/installation.html)
下面的部署会已MacOS为例子进行说明。

#### 2.配置工程关联Nginx配置

- 设置openresty工作目录为: `OPENRESTY_HOME=/usr/local/etc/openresty`
- `cd $OPENRESTY_HOME/nginx/conf` // 进入到openresty默认配置目录下
- 将bcs-projmgr/gateway目录下的内容复制到`$OPENRESTY_HOME/nginx/conf`目录下

#### 3.本地开发参数配置说明

- 修改`$OPENRESTY_HOME/nginx/conf/lua/init.lua.tpl` 中变量的值，并替换`$OPENRESTY_HOME/nginx/conf/lua/init.lua`文件,变量说明如下：

| 变量名 | 说明 |
|-------|------|
| __DEVOPS_STAITC_DIR__ | 前端静态文件的目录,默认值"$OPENRESTY_HOME/nginx/frontend" |
| __DEVOPS_LOGS_DIR__ | 访问access日志所在目录,默认值"$OPENRESTY_HOME/nginx/logs"|
| __BK_DOMAIN__ | 允许跨域的域名,默认值"\.bk\.com"|
| __DEVOPS_CONSUL_DNS_PORT__ | consul的DNS端口,默认值"8600" |
| __DEVOPS_CONSUL_DOMAIN__ | consul的域名,默认值"bkdevops" |

- 修改 `/usr/local/etc/openresty/nginx/conf/backend.conf.tpl` 中变量的值，并替换`/usr/local/etc/openresty/nginx/conf/backend.conf`文件,变量说明如下：

| 变量名 | 说明 |
|-------|------|
| __DEVOPS_HOST__ | 项目管理页面域名,默认值"dev.devops.bk.com" |

- 修改`/usr/local/etc/openresty/nginx/conf/frontend.conf.tpl` 中变量的值,并替换`/usr/local/etc/openresty/nginx/conf/frontend.conf`文件，变量说明如下：

| 变量名 | 说明 |
|-------|------|
| __DEVOPS_API_FQDN__ | 项目管理的后台接口域名,默认值"api.dev.devops.bk.com" |

- 修改 `/usr/local/etc/openresty/nginx/conf/devops.ssl.tpl` 中变量的值，并替换`/usr/local/etc/openresty/nginx/conf/devops.ssl`文件，变量说明如下：

| 变量名 | 说明 |
|-------|------|
| __DEVOPS_CRT__ | SSL证书crt文件路径,默认值"conf/cert/bk_domain.crt" |
| __DEVOPS_KEY__ | SSL证书key文件路径,默认值"conf/cert/bk_domain.key" |

#### 4.启动Nginx

- `cd /usr/local/etc/openresty/nginx` // 进入到openresty默认配置目录下（注意：加载是相对路径，所以一定要进入到nginx的目录下）
- `sudo sbin/nginx` // 启动nginx
- `sudo sbin/nginx -t` // 验证配置
- `sudo sbin/nginx -s reload` // 重新加载

#### 5.打开项目管理页面

打开 http://dev.devops.bk.com 即可进入项目管理页面。

---

### 三、Frontend(前端静态资源)的安装部署

#### 1. 安装依赖包

进入 frontend，执行以下命令安装依赖包

```shell
npm install .
```

#### 2. 本地开发参数配置说明

`项目管理和BCS APP的打通是通过修改下面的__BCS_APP_FQDN__变量来实现，将__BCS_APP_FQDN__替换本地启动的bcs-app的域名即可。`

- 修改 `frontend/src/assets/static/env.js.tpl` 中变量的值，并替换`frontend/src/assets/static/env.js`文件，变量说明如下：

| 变量名 | 说明 |
|-------|------|
| __DEVOPS_API_FQDN__ | 项目管理的后台接口域名,默认值"api.dev.devops.bk.com" |
| __PAAS_FQDN__ | 蓝鲸PAAS的外部域名,默认值"paas.bk.com" |
| __BCS_APP_FQDN__ | BCS APP的本地访问域名,默认值"bcs.bk.com" |


#### 3. 打包构建

在 frontend 目录下，继续执行以下命令打包前端静态资源，编译出来的文件会存放在`frontend/dist`目录下

```shell
npm run public
```

- 运行如下命令，进行本地开发

```shell
# 第一次运行时执行
npm run dll
# 启动命令
npm run dev
```

#### 4. 部署到Nginx上

在完成上一次的网关部署之后，将打包出来的内容`frontend/dist`复制到网关指定的静态文件目录`__DEVOPS_STAITC_DIR__/console`目录下。

---

### 四、PM（项目管理后台模块）的安装部署

#### 1.创建数据库

在mysql数据库中执行support-files/devops_pm.sql的命令，创建`devops_project`数据库。

#### 2.安装Gradle

参考安装Gradle官网安装方法：[Gradle安装指南](https://gradle.org/install/)。

#### 3.编译

- 编译出包命令

编译出来的包存放在`pm/release/service-project-1.0.0.jar`

```shell
gradle clean -DmysqlURL=__MYSQL_IP__:__MYSQL_PORT__ -DmysqlUser=__MYSQL_USERNAME__ -DmysqlPasswd=__MYSQL_PASSWORD__ :service:service-project:copyToRelease --profile
# 例子
# 默认参数
gradle clean :service:service-project:copyToRelease --profile
# 指定参数
gradle clean -DmysqlURL=127.0.0.1:3306 -DmysqlUser=root -DmysqlPasswd=mysql :service:service-project:copyToRelease --profile
```

- 编译启动命令

```shell
gradle -DmysqlURL=__MYSQL_IP__:__MYSQL_PORT__ -DmysqlUser=__MYSQL_USERNAME__ -DmysqlPasswd=__MYSQL_PASSWORD__ :service:service-project:bootRun --profile
# 例子
# 默认参数
gradle :service:service-project:bootRun --profile
# 指定参数
gradle -DmysqlURL=127.0.0.1:3306 -DmysqlUser=root -DmysqlPasswd=mysql :service:service-project:bootRun --profile
```

#### 4.本地开发参数配置说明

- 数据库编译参数修改，修改`pm/model/build.gradle.tpl`中变量的值，并替换`pm/model/build.gradle`文件

| 变量名 | 说明 |
|-------|------|
| __MYSQL_IP__ | mysql数据库IP地址,默认值"127.0.0.1" |
| __MYSQL_PORT__ | mysql数据库端口,默认值"3306" |
| __MYSQL_USER__ | mysql数据库账号,默认值"root" |
| __MYSQL_PASS__ | mysql数据库密码,默认值"mysql" |

- 运行日志参数修改，修改`pm/conf/log4j2.xml.tpl`中变量的值，并替换`pm/conf/log4j2.xml`文件

| 变量名 | 说明 |
|-------|------|
| __LOGGER_PATH__ | pm运行的日志,默认值"./logs" |

- pm进程编译参数修改，修改`pm/service/service-project/src/main/resources/application.yml.tpl`中变量的值，并替换`pm/service/service-project/src/main/resources/application.yml`文件

| 变量名 | 说明 |
|-------|------|
| __MYSQL_IP__ | mysql数据库IP地址,默认值"127.0.0.1" |
| __MYSQL_PORT__ | mysql数据库端口,默认值"3306" |
| __MYSQL_USER__ | mysql数据库账号,默认值"root" |
| __MYSQL_PASS__ | mysql数据库密码,默认值"mysql" |
| __CONSUL_AGENT_IP__ | mysql数据库密码,默认值"localhost" |
| __CONSUL_AGENT_PORT__ | mysql数据库密码,默认值"8500" |
| __DEVOPS_PM_PORT__ | pm进程启动端口,默认值"8065" |
| __PAAS_HOST__ | 蓝鲸PAAS的内部域名,默认值"paas.service.consul" |
| __PAAS_FQDN__ | 蓝鲸PAAS的外部域名,默认值"paas.bk.com" |
| __HTTP_SCHEMA__ | 蓝鲸企业版启动SCHEMA,默认值"https|http" |
| __IAM_HOST__ | 权限中心的内部域名,默认值"iam.service.consul" |
| __APP_CODE__ | 项目管理的APP_CODE,默认值"bkdevops" |
| __APP_TOKEN__ | 项目管理的APP_TOKEN,默认值"bkdevops" |

#### 5.启动jar包

```shell
java -Dlogger.config.file="./pm/conf/log4j2.xml" \
     -Dspring.datasource.url="jdbc:mysql://__MYSQL_IP__:__MYSQL_PORT__/devops_project?useSSL=false&autoReconnect=true&timezone=+800&useUnicode=true&characterEncoding=utf8&allowMultiQueries=true" \
     -Dspring.datasource.username="__MYSQL_USER__" \
     -Dspring.datasource.password="__MYSQL_PASS__" \
     -Dspring.cloud.consul.host="__CONSUL_AGENT_IP__" \
     -Dspring.cloud.consul.port="__CONSUL_AGENT_PORT__" \
     -Dserver.port="__DEVOPS_PM_PORT__" \
     -Dbk_login.path="http://__PAAS_HOST__/api/c/compapi/v2/bk_login/" \
     -Dbk_login.url="http://__PAAS_HOST__" \
     -Dbk_login.outurl="__HTTP_SCHEMA__://__PAAS_FQDN__" \
     -Dbk_login.bk_app_code="__APP_CODE__" \
     -Dbk_login.bk_app_secret="__APP_TOKEN__" \
     -Dauth.xBkAppCode="__APP_CODE__" \
     -Dauth.xBkAppSecret="__APP_TOKEN__"\
     -Dauth.url="http://__IAM_HOST__" \
     -Dbcs_cc.externalUrl="http://__PAAS_HOST__/api/apigw/bcs_cc/prod/project" \
     -jar "./pm/release/service-project-1.0.0.jar"

# 例子
# 默认参数
java -jar "./pm/release/service-project-1.0.0.jar"
# 指定参数
java -Dlogger.config.file="./pm/conf/log4j2.xml" \
     -Dspring.datasource.url="jdbc:mysql://127.0.0.1:3306/devops_project?useSSL=false&autoReconnect=true&timezone=+800&useUnicode=true&characterEncoding=utf8&allowMultiQueries=true" \
     -Dspring.datasource.username="root" \
     -Dspring.datasource.password="mysql" \
     -Dspring.cloud.consul.host="localhost" \
     -Dspring.cloud.consul.port="8500" \
     -Dserver.port="8065" \
     -Dbk_login.path="http://paas.service.consul/api/c/compapi/v2/bk_login/" \
     -Dbk_login.url="http://paas.service.consul" \
     -Dbk_login.outurl="https://paas.bk.com" \
     -Dbk_login.bk_app_code="bkdevops" \
     -Dbk_login.bk_app_secret="bkdevops" \
     -Dauth.xBkAppCode="bkdevops" \
     -Dauth.xBkAppSecret="bkdevops"\
     -Dauth.url="http://iam.service.consul" \
     -Dbcs_cc.externalUrl="http://paas.service.consul/api/apigw/bcs_cc/prod/project" \
     -jar "./pm/release/service-project-1.0.0.jar"
```
