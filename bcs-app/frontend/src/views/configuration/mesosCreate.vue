<template>
    <router-view :key="$route.path" v-if="isMesosCreate"></router-view>
    <div class="biz-content" v-else>
        <app-exception :type="'404'"></app-exception>
    </div>
</template>
<script>
    export default {
        data () {
            return {
                isProjectChange: false,
                isMesosCreate: true
            }
        },
        computed: {
            curProject () {
                const project = this.$store.state.curProject
                return project
            },
            applications () {
                return this.$store.state.mesosTemplate.applications
            },
            deployments () {
                return this.$store.state.mesosTemplate.deployments
            },
            services () {
                return this.$store.state.mesosTemplate.services
            },
            configmaps () {
                return this.$store.state.mesosTemplate.configmaps
            },
            secrets () {
                return this.$store.state.mesosTemplate.secrets
            },
            projectId () {
                return this.$route.params.projectId
            },
            onlineProjectList () {
                return this.$store.state.sideMenu.onlineProjectList
            }
        },
        mounted () {
            const createRoutes = [
                'mesosTemplatesetApplication',
                'mesosTemplatesetDeployment',
                'mesosTemplatesetService',
                'mesosTemplatesetConfigmap',
                'mesosTemplatesetSecret',
                'mesosTemplatesetIngress',
                'mesosTemplatesetHPA'
            ]
            const routeName = this.$route.name
            if (createRoutes.join(',').indexOf(routeName) < 0) {
                this.clearData()
            }
            this.checkProjectType()

            window.addEventListener('change::$currentProjectId', async e => {
                this.isProjectChange = true
            })
        },
        beforeRouteLeave (to, from, next) {
            // const self = this
            // let isEdited = false
            // this.applications.forEach(item => {
            //     if (item.isEdited) {
            //         isEdited = true
            //     }
            // })
            // this.deployments.forEach(item => {
            //     if (item.isEdited) {
            //         isEdited = true
            //     }
            // })
            // this.services.forEach(item => {
            //     if (item.isEdited) {
            //         isEdited = true
            //     }
            // })
            // this.configmaps.forEach(item => {
            //     if (item.isEdited) {
            //         isEdited = true
            //     }
            // })
            // this.secrets.forEach(item => {
            //     if (item.isEdited) {
            //         isEdited = true
            //     }
            // })

            // // 如果有数据变动或者自动保存产生版本变更
            // if (!this.isProjectChange && (isEdited || this.$store.state.mesosTemplate.canTemplateBindVersion)) {
            //     const store = this.$store
            //     store.commit('updateAllowRouterChange', false)
            //     this.$bkInfo({
            //         title: '确认',
            //         content: '确定要离开？数据未保存，离开后将会丢失',
            //         confirmFn () {
            //             store.commit('updateAllowRouterChange', true)
            //             self.clearData()
            //             next(true)
            //         }
            //     })
            //     next(false)
            // } else {
            //     this.clearData()
            //     next(true)
            // }
            this.clearData()
            next(true)
        },
        methods: {
            /**
             * 清空模板集数据
             */
            clearData () {
                this.$store.commit('mesosTemplate/clearCurTemplateData')
            },

            /**
             * 获取项目类型
             * @param  {number} id 项目ID
             * @return {number}  项目类型
             */
            async getProjectKind (id) {
                const curProject = this.curProject
                let kind = 0
                if (curProject && curProject.project_id === id) {
                    kind = curProject.kind
                } else {
                    const projects = this.onlineProjectList
                    for (const project of projects) {
                        if (project.project_id === id) {
                            kind = project.kind
                        }
                    }
                }
                return kind
            },

            /**
             * 查看项目类型
             */
            async checkProjectType () {
                const projectKind = await this.getProjectKind(this.projectId)
                
                if (projectKind === PROJECT_MESOS) {
                    this.isMesosCreate = true
                } else {
                    this.isMesosCreate = false
                }
            },

            /**
             * 重新刷新
             */
            reloadTemplateset () {
                this.isMesosCreate = false
                this.$nextTick(() => {
                    this.isMesosCreate = true
                })
            }
        }
    }
</script>
<style scoped>
    .biz-configuration-create-box {
        width: 100%;
    }
</style>
