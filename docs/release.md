# 发布日志
## release-1.5.7
#### 优化
- 调优计算 iam_ns_id 的方法

#### 修复
- 无法删除集群的问题


## release-1.5.6
#### 新增
- 权限细粒度控制：支持集群、命名空间和模板集
- 资源视图功能：支持对命名空间，应用负载等 K8S 资源的页面化操作
- Pod 标准输出日志查询
- 跨域请求来源限制


## release-1.4.5
#### 修复
- [#951](https://github.com/Tencent/bk-bcs-saas/pull/951)修复由于CMDB主机列表接口返回字段(bk_cloud_id)类型变动导致的问题
- [#941](https://github.com/Tencent/bk-bcs-saas/pull/941)修复用户是超级管理员时，项目权限异常的问题

#### 优化
- Mesos允许通过prometheus获取集群和节点metric功能


## release-1.4.1
#### 新增
- Helm 命令支持 --wait 参数

#### 优化
- [#867](https://github.com/Tencent/bk-bcs-saas/pull/867)后台任务轮训模块及API返回错误码
- Mesos模板集: 优化模板集的导入导出功能
- Mesos删除节点: 忽略bcs-system命名空间下的资源


## release-1.3.24

#### 新增
- 开放Metric管理功能

#### 优化
- [#793](https://github.com/Tencent/bk-bcs-saas/pull/793) HPA: k8s hpa client 替换为 dynamic client


## release-1.3.23

#### 修复
- [#834](https://github.com/Tencent/bk-bcs-saas/pull/834)修复前端paste事件没有过滤\r问题

#### 更新
- 更新查询CMDB业务下主机信息接口


## release-1.3.22

#### 修复
- [#824](https://github.com/Tencent/bk-bcs-saas/pull/824)Mesos集群节点标签过滤的问题

## release-1.3.21

#### 新增
- 纳管用户已有集群功能
- 集成 K8S 应用包管理工具 Helm
- 支持 kubectl 命令行工具的 WebConsole 服务

#### 更新
- 升级项目权限体系，对接蓝鲸权限中心3.0
