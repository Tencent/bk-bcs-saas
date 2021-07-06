# 蓝鲸智云容器管理平台SaaS
![](docs/resource/logo/bk_bcs.png)
---
[![license](https://img.shields.io/badge/license-mit-brightgreen.svg?style=flat)](https://github.com/Tencent/bk-bcs-saas/blob/master/LICENSE) [![Release Version](https://img.shields.io/badge/release-1.3.23-brightgreen.svg)](https://github.com/Tencent/bk-bcs-saas/releases) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Tencent/bk-bcs-saas/pulls) [![BK Pipelines Status](https://api.bkdevops.qq.com/process/api/external/pipelines/projects/cc/p-c02db56ac633447eb2e740b3fd0b6d2b/badge?X-DEVOPS-PROJECT-ID=cc)](https://api.bkdevops.qq.com/process/api/external/pipelines/projects/bcs/p-c03c759b697f494ab14e01018eccb052/badge?X-DEVOPS-PROJECT-ID=bcs) [![](https://travis-ci.com/Tencent/bk-bcs-saas.svg?token=ypkHQqxUR3Y3ctuD7qFS&branch=master)](https://travis-ci.com/Tencent/bk-bcs-saas)


[(English Documents Available)](readme_en.md)

> **重要提示**: `master` 分支是开发分支，可能处于 *不稳定或者不可用状态* 。请通过[releases](https://github.com/tencent/bk-bcs-saas/releases) 而非 `master` 去获取稳定的软件包

蓝鲸智云容器管理平台(BCS，BlueKing Container Service)是高度可扩展、灵活易用的容器管理服务。蓝鲸容器管理平台支持两种不同的集群模式，分别为原生Kubernetes模式和基于Mesos自研的模式。使用该平台，用户无需关注基础设施的安装、运维和管理，只需要调用简单的API，或者在页面上进行简单的配置，便可对容器进行启动、停止等操作，查看集群、容器及服务的状态，以及使用各种组件服务。用户可以依据自身的需要选择集群模式和容器编排的方式，以满足业务的特定要求。

本次开源的是蓝鲸智云容器管理平台的SaaS，它提供了友好的操作界面，支持对项目集群、节点、命名空间、部署配置、仓库镜像、应用等进行可视化界面操作管理，并提供了WebConsole可快捷查看集群状态的命令行服务，针对K8S集群模式支持使用Helm进行K8S应用的部署和管理。

蓝鲸智云容器管理平台的SaaS源码包含:
- bcs-app：SaaS产品层主体功能模块，负责项目集群、节点、命名空间、部署配置、仓库镜像、应用等进行可视化界面操作管理，以及WebConsole、Helm等服务
- bcs-cc：配置中心模块，负责集群版本、快照等信息管理
- bcs-projmgr：项目信息管理模块，负责项目创建及基本信息管理

## Overview

- [架构设计](docs/overview/architecture.md)
- [代码目录](docs/overview/project_codes.md)
- [部署拓扑](docs/overview/project_deploy.md)

## Features
- **集群管理**：支持自定义设定Master和Node节点，一键自动安装集群组件，按业务架构划分集群，保证安全可靠。支持动态伸缩，可以实时添加/剔除集群节点，支持集群和节点级别的监控告警及主要数据的视图展示
- **模板管理**：支持模板集的多版本管理，支持通过命名空间管理不同的环境
- **应用管理**：通过应用视图或者命名空间视图管理容器，查看应用、POD、容器等的在线状态。启停容器，重新调度容器，对应用做扩缩容、滚动升级等更新操作
- **镜像管理**：对接harbor镜像仓库，镜像信息在线管理
- **网络管理**：查看服务的列表，以及每个服务的详细信息，对服务进行操作，例如更新服务或者停止服务。查看线上负载均衡器列表，及每个负载均衡器的详细信息，启动、删除或者更新负载均衡器
- **WebConsole**：快捷查看集群状态的命令行工具服务
- **Helm**：支持K8S应用的部署和管理工具Helm

详细介绍请参考[功能说明](https://docs.bk.tencent.com/bcs/)


## Getting started

- [本地安装部署指引](/docs/install/dev-install-overview.md)
- [用开源版替换社区版](https://docs.bk.tencent.com/bk_osed/Open-Bcs.html#open_bcs)

## Roadmap

- [版本日志](docs/release.md)

## Support

- [产品白皮书](https://docs.bk.tencent.com/bcs/)
- [蓝鲸论坛](https://bk.tencent.com/s-mart/community)
- 联系我们，技术交流QQ群：
<img src="docs/resource/img/QR-Code.png" width="250" hegiht="250" align=center />

## BlueKing Community
- [BK-CI](https://github.com/Tencent/bk-ci)：蓝鲸持续集成平台是一个开源的持续集成和持续交付系统，可以轻松将你的研发流程呈现到你面前。
- [BK-BCS](https://github.com/Tencent/bk-bcs)：蓝鲸容器管理平台是以容器技术为基础，为微服务业务提供编排管理的基础服务平台。
- [BK-CMDB](https://github.com/Tencent/bk-cmdb)：蓝鲸配置平台（蓝鲸CMDB）是一个面向资产及应用的企业级配置管理平台。
- [BK-PaaS](https://github.com/Tencent/bk-PaaS)：蓝鲸PaaS平台是一个开放式的开发平台，让开发者可以方便快捷地创建、开发、部署和管理SaaS应用。
- [BK-SOPS](https://github.com/Tencent/bk-sops)：标准运维（SOPS）是通过可视化的图形界面进行任务流程编排和执行的系统，是蓝鲸体系中一款轻量级的调度编排类SaaS产品。

## Contributing
对于项目感兴趣，想一起贡献并完善项目请参阅[Contributing Guide](docs/CONTRIBUTING.md)。

[腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者的参与和贡献，期待你的加入。

## FAQ

请查看 [FAQ](docs/faq.md)

## License

基于 MIT 协议， 详细请参考[LICENSE](LICENSE.txt)
