<template>
    <div class="biz-cluster-content" :class="curProject.kind === PROJECT_MESOS || curProject.kind === PROJECT_TKE ? 'more-info' : ''">
        <div class="biz-progress-box">
            <div class="progress-header">
                <span class="title">{{$t('CPU使用率')}}</span>
                <span class="percent" v-if="!loading">
                    {{$parent.conversionPercent(curCluster.cpu_usage.used, curCluster.cpu_usage.total)}}%
                </span>
            </div>
            <div class="progress" :class="loading ? 'loading' : ''">
                <!-- <div class="progress loading"> -->
                <div class="progress-bar primary" v-if="loading" style="width: 0%"></div>
                <div class="progress-bar primary" v-else
                    :style="{ width: `${$parent.conversionPercent(curCluster.cpu_usage.used, curCluster.cpu_usage.total)}%` }"></div>
            </div>
        </div>
        <div class="biz-progress-box">
            <div class="progress-header">
                <span class="title">{{$t('内存使用率')}}</span>
                <span class="percent" v-if="!loading">
                    {{$parent.conversionPercent(curCluster.mem_usage.used_bytes, curCluster.mem_usage.total_bytes)}}%
                </span>
            </div>
            <div class="progress" :class="loading ? 'loading' : ''">
                <!-- <div class="progress loading"> -->
                <div class="progress-bar success" v-if="loading" style="width: 0%"></div>
                <div class="progress-bar success" v-else :style="{ width: `${$parent.conversionPercent(curCluster.mem_usage.used_bytes, curCluster.mem_usage.total_bytes)}%` }"></div>
            </div>
        </div>
        <div class="biz-progress-box">
            <div class="progress-header">
                <span class="title">{{$t('磁盘使用率')}}</span>
                <span class="percent" v-if="!loading">
                    {{$parent.conversionPercent(curCluster.disk_usage.used_bytes, curCluster.disk_usage.total_bytes)}}%
                </span>
            </div>
            <div class="progress" :class="loading ? 'loading' : ''">
                <!-- <div class="progress loading"> -->
                <div class="progress-bar warning" v-if="loading" style="width: 0%"></div>
                <div class="progress-bar warning" v-else :style="{ width: `${$parent.conversionPercent(curCluster.disk_usage.used_bytes, curCluster.disk_usage.total_bytes)}%` }"></div>
            </div>
        </div>
        <div class="biz-progress-box" v-if="curProject.kind === PROJECT_TKE">
            <div class="progress-header">
                <span class="title">{{$t('集群IP')}}</span>
                <span class="percent" v-if="!loading">
                    {{curCluster.ip_resource_total === 0 ? 0 : `${curCluster.ip_resource_used} / ${curCluster.ip_resource_total}`}}
                </span>
            </div>
            <div class="progress" :class="loading ? 'loading' : ''">
                <div class="progress-bar warning" v-if="loading" style="width: 0%"></div>
                <div class="progress-bar warning" v-else :style="{ width: `${curCluster.ip_resource_total === 0 ? 0 : $parent.conversionPercent(curCluster.ip_resource_total - curCluster.ip_resource_used, curCluster.ip_resource_total)}%` }"></div>
            </div>
        </div>
        <div class="biz-progress-box" v-if="curProject.kind === PROJECT_MESOS">
            <div class="progress-header">
                <span class="title">{{$t('集群IP')}}</span>
                <span class="percent">
                    {{curCluster.allip === 0 ? 0 : `${curCluster.activeip} / ${curCluster.allip}（${$t('剩余')}${curCluster.availableip}）`}}
                </span>
            </div>
            <div class="progress">
                <div class="progress-bar warning" :style="{ width: `${curCluster.allip === 0 ? 0 : $parent.conversionPercent(curCluster.activeip, curCluster.allip, true)}%` }"></div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        props: {
            curProject: {
                type: Object
            },
            curCluster: {
                type: Object
            },
            // curClusterIndex: {
            //     type: Number
            // },
            // overviewList: {
            //     type: Array
            // },
            loading: {
                type: Boolean
            }
        },
        data () {
            return {
                PROJECT_MESOS: window.PROJECT_MESOS,
                PROJECT_TKE: window.PROJECT_TKE
            }
        },
        // watch: {
        //     loading (v) {
        //         console.error(v)
        //     }
        // },
        created () {
        },
        beforeDestroy () {
        },
        methods: {
        }
    }
</script>

<style lang="postcss">
    @import './status-progress.css';
</style>
