<template>
    <component :is="componentName"></component>
</template>

<script>
    const wlistMetric = () => import(
        /* webpackChunkName: 'metric' */'./main'
    )

    const metric = () => import(
        /* webpackChunkName: 'metric' */'./metric-main'
    )

    export default {
        components: {
            wlistMetric,
            metric
        },
        data () {
            return {
                componentName: 'wlistMetric'
            }
        },
        computed: {
            curProject () {
                return this.$store.state.curProject
            }
        }
        // mounted () {
        //     this.setComponent()
        // },
        // methods: {
        //     /**
        //      * 设置动态组件
        //      */
        //     setComponent () {
        //         const funcWlist = this.curProject.func_wlist
        //         if (funcWlist && funcWlist.length && funcWlist.indexOf('ServiceMonitor') > -1) {
        //             this.componentName = 'wlistMetric'
        //         } else {
        //             this.componentName = 'metric'
        //         }
        //     }
        // }
    }
</script>
