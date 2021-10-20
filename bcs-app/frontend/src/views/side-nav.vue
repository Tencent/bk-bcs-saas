<template>
    <div>
        <p class="biz-side-title">
            <img src="@/images/bcs2.svg" class="all-icon">
            <span style="font-size: 16px;">{{$t('容器服务')}}</span>
            <i class="biz-conf-btn bcs-icon bcs-icon-cog" style="font-size: 16px;"
                v-bk-tooltips.bottom="$t('项目信息')" @click="handleShowProjectConfDialog "></i>
        </p>
        <!-- 菜单 -->
        <div class="side-nav">
            <SideMenu :list="menuList" :selected="selected" @change="handleMenuChange"></SideMenu>
            <p class="biz-copyright">Copyright © 2012-{{(new Date()).getFullYear()}} Tencent BlueKing. All Rights Reserved</p>
        </div>
        <ProjectConfig v-model="isProjectConfDialogShow"></ProjectConfig>
    </div>
</template>

<script lang="ts">
    import { defineComponent, computed, ref } from '@vue/composition-api'
    import SideMenu from '@/components/menu/index.vue'
    import { IMenuItem, ISpecialMenuItem } from '@/store/menu'
    import ProjectConfig from '@/views/project/project-config.vue'

    export default defineComponent({
        name: 'SideNav',
        components: {
            SideMenu,
            ProjectConfig
        },
        setup (props, ctx) {
            const { $store, $router } = ctx.root

            const featureFlag = computed(() => {
                return $store.getters.featureFlag || {}
            })
            const menuConfigList = computed<IMenuItem[]>(() => {
                return $store.state.menuList
            })
            const menuList = computed(() => {
                return menuConfigList.value.reduce<(IMenuItem | ISpecialMenuItem)[]>((pre, item) => {
                    if (item.id && featureFlag.value[item.id]) {
                        pre.push(item)
                    } else if (!item.id) {
                        pre.push(item)
                    }
                    return pre
                }, [])
            })

            const selected = computed(() => {
                // 当前选择菜单在全局导航守卫中设置的
                return $store.state.curMenuId
            })
            const projectCode = computed(() => {
                return $store.state.curProjectCode
            })
            const projectId = computed(() => {
                return $store.state.curProjectId
            })
            // 菜单切换
            const handleMenuChange = (item: IMenuItem) => {
                // 直接取$route会存在缓存，需要重新从root上获取最新路由信息
                if (ctx.root.$route.name === item.routeName) return

                if (item.id === 'MONITOR') {
                    // 特殊处理监控中心
                    window.open(`${window.DEVOPS_HOST}/console/monitor/${projectCode.value}/?project_id=${projectId.value}`)
                } else {
                    $router.push({
                        name: item.routeName
                    })
                }
            }
            const isProjectConfDialogShow = ref(false)
            const handleShowProjectConfDialog = () => {
                isProjectConfDialogShow.value = true
            }

            return {
                menuList,
                selected,
                handleMenuChange,
                isProjectConfDialogShow,
                handleShowProjectConfDialog
            }
        }
    })
</script>

<style scoped lang="postcss">
    .biz-side-title {
        position: relative;
    }
    .cluster-selector {
        background: #fafbfd;
    }
    .resouce-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px 0;
        .tab {
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f7f8f9;
            border: 1px solid #dde4eb;
            margin-left: -1px;
            font-size: 12px;
            height: 24px;
            padding: 0 26px;
            cursor: pointer;
            white-space: nowrap;
            &.active {
                background: #fff;
                color: #3a84ff;
            }
            &.disabled {
                cursor: not-allowed;
            }
            &:first-child {
                border-radius: 3px 0 0 3px;
            }
            &:last-child {
                border-radius: 0 3px 3px 0;
            }
        }
    }
    .biz-conf-btn {
        position: absolute;
        right: 10px;
        top: 16px;
        font-size: 12px;
        cursor: pointer;
        width: 30px;
        height: 30px;
        text-align: center;
        line-height: 30px;
        z-index: 100;
    }
    .cluster-name {
        max-width: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: inline-block;
        white-space: nowrap;
        margin-top: 2px;
    }
    .cluster-name-all {
        font-size: 16px;
    }
    .dot {
        position: absolute;
        display: inline-block;
        width: 16px;
        height: 16px;
        top: 16px;
        right: 4px;
        z-index: 1;
        padding: 2px;
    }
</style>
