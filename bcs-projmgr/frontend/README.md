### 蓝盾devops平台——服务接入

> test环境： http://bking.com

#### iframe接入

> 点击目标导航，界面加载iframe装载对应业务url。 并提供内外层通信的API来保证体验一致性，提升iframe下用户体验。

+ 建议选择蓝鲸提供的UI框架组件，更快速开发，同时保证ui体验的一致性

+ 优势：1.独立少耦合，易维护，独立发布

+ 缺陷：1.体验不容易做到完全统一；2.内外层通信，开发复杂性相对高


#####  蓝鲸智云容器管理平台导航模块

在src/assets/static/env.js 文件配置相关域名信息

出包命令 npm run public

本地调试：
如果是在本地先一次运行，执行npm run dll命令，
然后执行npm run dev

然后访问127.0.0.1:80/console  即可访问（运行端口可在webpack.config.js文件修改）


