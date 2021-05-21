<template>
    <div class="biz-cluster-content" :class="curCluster.type === 'mesos' ? 'more-info' : ''">
        <template v-if="curCluster.type === 'mesos' && curCluster.func_wlist && curCluster.func_wlist.indexOf('MesosResource') > -1">
            <div class="biz-progress-box" style="margin-bottom: 15px;">
                <div class="progress-header" style="margin-bottom: 2px;">
                    <span class="title">{{$t('IP数量(个)')}}</span>
                </div>
                <div style="margin-bottom: 2px;">
                    {{curCluster.activeip}} / {{curCluster.availableip + curCluster.activeip}}（剩余{{curCluster.availableip}}）
                </div>
                <div class="progress" :class="loading ? 'loading' : ''">
                    <div class="progress-bar primary" v-if="loading" style="width: 0%"></div>
                    <div class="progress-bar primary" v-else
                        :style="{ width: `${$parent.conversionPercent(curCluster.activeip, curCluster.availableip + curCluster.activeip)}%` }"></div>
                </div>
            </div>
            <div class="biz-progress-box" style="margin-bottom: 15px;">
                <div class="progress-header" style="margin-bottom: 2px;">
                    <span class="title">{{$t('CPU数量(核)')}}</span>
                </div>
                <div style="margin-bottom: 2px;">
                    {{(curCluster.cpu_usage.total - curCluster.cpu_usage.remain).toFixed(2)}} / {{curCluster.cpu_usage.total}}（剩余{{parseFloat(curCluster.cpu_usage.remain).toFixed(2)}}）
                </div>
                <div class="progress" :class="loading ? 'loading' : ''">
                    <div class="progress-bar success" v-if="loading" style="width: 0%"></div>
                    <div class="progress-bar success" v-else
                        :style="{ width: `${$parent.conversionPercent(curCluster.cpu_usage.total - curCluster.cpu_usage.remain, curCluster.cpu_usage.total)}%` }"></div>
                </div>
            </div>
            <div class="biz-progress-box" style="margin-bottom: 15px;">
                <div class="progress-header" style="margin-bottom: 2px;">
                    <span class="title">{{$t('内存数量(GB)')}}</span>
                </div>
                <div style="margin-bottom: 2px;">
                    {{(curCluster.mem_usage.total / 1024 - curCluster.mem_usage.remain / 1024).toFixed(2)}} / {{(curCluster.mem_usage.total / 1024).toFixed(2)}}（剩余{{(curCluster.mem_usage.remain / 1024).toFixed(2)}}）
                </div>
                <div class="progress" :class="loading ? 'loading' : ''">
                    <div class="progress-bar warning" v-if="loading" style="width: 0%"></div>
                    <div class="progress-bar warning" v-else
                        :style="{ width: `${$parent.conversionPercent((curCluster.mem_usage.total / 1024 - curCluster.mem_usage.remain / 1024), curCluster.mem_usage.total / 1024)}%` }"></div>
                </div>
            </div>
            <div style="margin-bottom: 10px; height: 1px;"></div>
        </template>
        <template v-else>
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
            <div class="biz-progress-box" v-if="curCluster.type === 'mesos'">
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
            <div class="biz-progress-box" v-if="curCluster.type === 'mesos'">
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
        </template>
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
