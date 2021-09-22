<template>
    <section class="create-form-cluster">
        <FormGroup :title="$t('基本信息')">
            <bcs-form :label-width="100">
                <bcs-form-item :label="$t('集群名称')" required>
                    <bcs-input></bcs-input>
                </bcs-form-item>
                <bcs-form-item :label="$t('集群环境')" required>
                    <bcs-radio-group>
                        <bcs-radio>
                            {{ $t('测试环境') }}
                        </bcs-radio>
                        <bcs-radio>
                            {{ $t('正式环境') }}
                        </bcs-radio>
                    </bcs-radio-group>
                </bcs-form-item>
                <bcs-form-item :label="$t('模板名称')" required>
                    <div class="template-name">
                        <bcs-select></bcs-select>
                        <bcs-button text class="ml10">{{ $t('新增集群模板') }}</bcs-button>
                    </div>
                </bcs-form-item>
                <bcs-form-item :label="$t('描述')">
                    <bcs-input></bcs-input>
                </bcs-form-item>
            </bcs-form>
        </FormGroup>
        <FormGroup :title="$t('集群选项')" class="mt15">
            <template #title>
                <div class="bk-button-group">
                    <bcs-button @click="handleChangeMode('form')" :class="createMode === 'form' ? 'is-selected' : ''" size="small">{{ $t('表单结构') }}</bcs-button>
                    <bcs-button @click="handleChangeMode('yaml')" :class="createMode === 'yaml' ? 'is-selected' : ''" size="small">{{ $t('Yaml格式') }}</bcs-button>
                </div>
            </template>
            <template #default>
                <FormMode v-if="createMode === 'form'"></FormMode>
                <YamlMode v-else></YamlMode>
            </template>
        </FormGroup>
        <FormGroup :title="$t('选择Master')" :desc="$t('仅支持数量为3,5和7个')" class="mt15">
            <template #title>
                <bcs-button text v-if="ipList.length">
                    <i class="bcs-icon bcs-icon-plus"></i>
                    {{ $t('选择服务器') }}
                </bcs-button>
            </template>
            <div class="choose-server-btn" @click.stop="handleOpenSelector" v-if="!ipList.length">
                <i class="bcs-icon bcs-icon-plus"></i>
                <span>{{ $t('选择服务器') }}</span>
            </div>
            <div class="choose-server-list" v-else>
                <bcs-table :data="ipList">
                    <bcs-table-column type="index" :label="$t('序列')" width="60"></bcs-table-column>
                    <bcs-table-column :label="$t('内网IP')"></bcs-table-column>
                    <bcs-table-column :label="$t('机房')" prop=""></bcs-table-column>
                    <bcs-table-column :label="$t('机型')" prop=""></bcs-table-column>
                    <bcs-table-column :label="$t('操作')" prop="">
                        <template #default="{ row }">
                            <bcs-button text @click="handleDeleteIp(row)">{{ $t('移除') }}</bcs-button>
                        </template>
                    </bcs-table-column>
                </bcs-table>
            </div>
        </FormGroup>
        <IpSelector v-model="showIpSelector" @confirm="handleChooseServer"></IpSelector>
    </section>
</template>
<script lang="ts">
    import { defineComponent, ref } from '@vue/composition-api'
    import FormGroup from './form-group.vue'
    import FormMode from './form-mode.vue'
    import YamlMode from './yaml-mode.vue'

    export default defineComponent({
        name: 'CreateFormCluster',
        components: {
            FormGroup,
            FormMode,
            YamlMode
        },
        setup (props, ctx) {
            const createMode = ref<'form' | 'yaml'>('form')
            // 更改集群选项模式
            const handleChangeMode = (mode) => {
                createMode.value = mode
            }

            const showIpSelector = ref(false)
            // 打开IP选择器
            const handleOpenSelector = () => {
                showIpSelector.value = true
            }
            // 选择IP节点
            const ipList = ref<any[]>([{}])
            const handleChooseServer = (data = []) => {
                ipList.value = data
            }
            const handleDeleteIp = (row) => {
                const index = ipList.value.findIndex(item => item.bk_host_innerip === row.bk_host_innerip)
                index > -1 && ipList.value.splice(index, 1)
            }
            return {
                createMode,
                showIpSelector,
                ipList,
                handleChangeMode,
                handleOpenSelector,
                handleChooseServer,
                handleDeleteIp
            }
        }
    })
</script>
<style lang="postcss" scoped>
.create-form-cluster {
    padding: 24px;
    /deep/ .bk-input-text {
        width: 400px;
    }
    /deep/ .bk-select {
        width: 400px;
    }
    .template-name {
        display: flex;
    }
    .cluster-config {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        .title {
            font-size: 14px;
            font-weight: 700;
            line-height: 22px;
        }
    }
    .choose-server-btn {
        border: 1px dashed #c4c6cc;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #3A84FF;
        width: 630px;
        margin-left: 24px;
        &:hover {
            border-color: #3A84FF;
            cursor: pointer;
        }
    }
    .choose-server-list {
        padding-left: 24px;
    }
}
</style>
