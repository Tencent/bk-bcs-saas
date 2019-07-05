<template>
    <div class="biz-actions" v-clickoutside="hide">
        <bk-tooltip :content="'快速入门'" placement="bottom">
            <a class="button" href="javascript:void(0)" @click.stop.prevent="showGuide">
                <i class="bk-icon icon-calendar"></i>
            </a>
        </bk-tooltip>
        <transition name="fadeRight">
            <div :class="['biz-cluster-guide', { 'show': visibility }]" v-show="visibility" @mouseenter="mouseoverHandler" @mouseleave="mouseoutHandler">
                <h1 class="title">蓝鲸容器服务使用教程</h1>
                <div class="guide-page" v-if="curStep === 'step1'">
                    <p class="text">本教程将向您简单介绍如何使用蓝鲸容器服务</p>
                    <p class="text">
                        <strong>以下是您操作的主要步骤：</strong>
                    </p>
                    <dl>
                        <dt>1、新建集群</dt>
                        <dd>点击导航“集群” -> “新建集群”，需要选择Master节点主机（主机信息来源于CMDB），创建集群，确定创建后，系统将进行集群初始化操作</dd>
                        <dt>2、集群增加Node节点</dt>
                        <dd>进入指定集群 => 节点列表，选择添加节点即可</dd>
                        <dt>3、项目镜像管理</dt>
                        <dd>点击导航“仓库” => “项目镜像”，按文档“如何推镜像”指引将项目镜像推至仓库</dd>
                    </dl>
                    <div class="operate">
                        <button class="bk-button bk-primary" @click="goStep('step2')">继续</button>
                        <button class="bk-button bk-danger" @click="hide">关闭</button>
                    </div>
                </div>
                <div class="guide-page" v-if="curStep === 'step2'">
                    <dl>
                        <dt>4、创建命名空间</dt>
                        <dd>点击导航“命名空间”，新建命名空间，指定命名空间所属集群</dd>
                        <dt>5、创建模板集</dt>
                        <dd>点击导航“模板集”，新建模板集。<br />
                            模板集指您接入容器服务的业务模块所包含的Mesos或Kubernetes资源配置，我们将以模板的形式供您可持续编辑，分版本保存。<br />
                            您可以通过Json或Yaml文件导入的方式将已有服务的资源配置导入模板，再次进行编辑并保存</dd>
                    </dl>
                    <div class="operate">
                        <button class="bk-button bk-primary" @click="goStep('step3')">继续</button>
                        <button class="bk-button bk-primary" @click="goStep('step1')">返回</button>
                        <button class="bk-button bk-danger" @click="hide">关闭</button>
                    </div>
                </div>
                <div class="guide-page" v-if="curStep === 'step3'">
                    <dl>
                        <dt>6、模板实例化</dt>
                        <dd>保存模板后，点击实例化按钮，选择模板集、具体资源模板以及指定集群的命名空间，系统将生成对应的资源配置文件（Json\Yaml）供您检查。<br />
                            点击“创建”按钮后，系统将下发资源配置文件到指定集群，创建应用实例。</dd>
                        <dt>7、应用实例详情</dt>
                        <dd>点击导航“应用”，您将看到具体的实例信息，可在线做滚动升级、扩缩容等操作。</dd>
                    </dl>
                    <div class="operate">
                        <button class="bk-button bk-primary" @click="goStep('step2')">返回</button>
                        <button class="bk-button bk-danger" @click="hide">关闭</button>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>

<script>
    import clickoutside from '@open/directives/clickoutside'

    export default {
        directives: {
            clickoutside
        },
        props: {
            isShow: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const isShow = this.isShow
            return {
                curStep: 'step1',
                visibility: isShow,
                steps: ['step1', 'step2']
            }
        },
        methods: {
            show () {
                this.visibility = true
                this.$emit('status-change', this.visibility)
            },
            hide () {
                this.visibility = false
                this.$emit('status-change', this.visibility)
                document.body.style.overflow = 'auto'
            },
            goStep (stepId) {
                this.curStep = stepId
            },
            /**
             * 显示快速入门侧边栏
             */
            showGuide () {
                this.show()
            },
            mouseoverHandler () {
                document.body.style.overflow = 'hidden'
            },
            mouseoutHandler () {
                document.body.style.overflow = 'auto'
            },
            /**
             * 切换快速入门侧边栏状态
             *
             * @param {boolean} status 状态
             */
            toggleGuide (status) {
                this.isShowGuide = status
            }
        }
    }
</script>

<style>
    @import './index.css';
</style>
