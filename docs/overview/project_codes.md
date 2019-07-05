# 蓝鲸智云容器管理平台SaaS代码结构
目前, 蓝鲸智云容器管理平台SaaS源码组成如下：
```
bk-bcs-saas
├── bcs-cc
├── bcs-app
│   ├── README.md
│   ├── app.yml
│   ├── backend
│   ├── bk_bcs_app.png
│   ├── frontend
│   ├── manage.py
│   ├── requirements-dev.txt
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── scripts
│   └── wsgi.py
└── bcs-projmgr
    ├── README.md
    ├── frontend
    ├── gateway
    ├── pm
    └── support-files
```
- bcs-cc: 配置中心模块，负责管理集群节点、版本快照等信息

- bcs-app: 容器服务产品层主体功能模块，实现了集群管理、模板集、WebConsole等容器管理功能
    - frontend: 容器服务产品前端
    - backend: 容器服务产品后端
    - app.yml: bk-PaaS托管用的配置文件
    - scripts: 部署到生产环境时的打包脚本
    - runtime.txt: bcs-app依赖的python版本
    - requirements-dev.txt: 本地开发用的额外软件包

- bcs-projmgr: 项目信息管理模块，负责项目创建及基本信息管理
    - frontend: 项目管理的前端静态页面
    - gateway: 项目管理的接入层
    - pm: 项目管理后端模块