# 蓝鲸容器管理平台配置中心（BCS-CC）安装部署文档

## 系统要求
- 数据库: mysql
- Go: 版本1.9及以上

## 本地开发环境搭建步骤

#### 1. 基础环境安装
安装配置Golang环境，参考[Golang安装指引](http://docs.studygolang.com/doc/install)

#### 2. 本地开发
如果需要修改源码，可参考以下步骤进行，或直接进入第3步编译源码
- 在`bcs-cc/configcenter/apis`目录下创建自己的文件，比如`test.go`
- 在`test.go`中添加自己的逻辑
- 在`bcs-cc/configcenter/urlrouter.go`下面添加自己的路由

#### 3. 编译源码
```
# 进入项目根目录
cd bcs-cc
# 执行编译命令，会创建src, bin，pkg三个目录，其中二进制在bin目录下生成
make
# 查看help命令
bin/bcs_cc help
```

#### 4. 配置启动参数
配置文件为etc/dev.yaml，内容及说明如下
```
version: v1.0.0
location: Local
debug: true      # 是否开启gin debug模式
run_env: "dev"   # 本地开发测试，设置为dev
available_environment_flags:
    - prod
database:
  type: mysql
  host: 127.0.0.1           # 数据库地址
  port: 3306                # 端口
  user:                     # 访问用户名
  password: ""              # 密码
  db_name:                  # 访问db名称
  charset: utf8
  max_idle_conns: 10
  max_open_conns: 100
confcenter:
  host: 127.0.0.1                   # 启动服务的IP，本地直接使用127.0.0.1即可
  port: 8080                        # 启动服务的端口
logging:
  level: info                       # 日志级别
  file_dir: "/data/logs/bcs-cc"     # 日志目录
  stderr: true
  log_to_redis: false
authconf:                                                                          # 访问IAM的相关配置
  host: ""                                                                         # 访问IAM的域名，参照社区版IAM配置
  proxy: ""                                                                        # 根据网络，设置代理，默认无代理 
  auth_token_path: "/bkiam/api/v1/auth/access-tokens"                              # 生成access_token的路径
  auth_project_path: "/bkiam/api/v1/perm/scope_type/project/authorized-scopes/"    # 获取有权限项目路径
  auth_verify_path: "/bkiam/api/v1/auth/access-tokens/verify"                      # 校验用户登录态，主要是获取应用编码及用户名
apigwconf:                      # 访问APIGW的相关配置
  identity_from_jwt: true       # 认证信息是否来源于apigw传递的jwttoken，如果为true，则通过jwttoken获取应用编码及用户名；否则，通过accesstoken解析应用编码及用户名
  host: ""                      # 访问apigw的域名，参照社区版apigw配置
  proxy: ""                     # 根据网络，设置代理，默认无代理                            
interval: 300
disable_encrypt: true
enable_cluster_metric: true                                             # 是否开启集群资源metric采集，默认开启；本地开发可以关闭
app_code: "bk_bcs"                                                      # 访问其它系统需要的app_code，参照社区版配置
app_secret: "d8198f0d-014d-403d-a3ac-8a2044823aaf"                      # 访问其它系统需要的app_secret，参照社区版配置
jwt_path: ""                                                            # 从apigw获取的公钥文件存放路径，默认在config/cert下
```

注意：参照社区版配置，根据自己的环境，替换相应的参数值，才能正常运行服务

#### 5. 初始化数据库
- 创建配置中心需要的表结构：

```
bin/bcs_cc migrate -c etc/dev.yaml
```

- 导入数据：创建集群时，需要添加区域、集群版本配置信息，可以参考社区版数据导入

#### 6. 启动服务
初始化数据库表后，启动配置中心服务
```
bin/bcs_cc cc -c etc/dev.yaml
```
注意: 如果想要提供其他系统访问，建议注册到apigw，具体参考`社区版apigw`使用文档

## 部署 BCS-CC 到生产环境

#### 1. 编译
参考`编译源码`步骤，编译二进制文件；如果已编译，可忽略此步

#### 2. 替换的社区版
参考[开源bk-bcs-saas替换社区版部署指南](xxx)替换BCS-CC