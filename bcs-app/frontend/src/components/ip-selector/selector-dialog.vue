<template>
    <bcs-dialog class="selector-dialog"
        :mask-close="false"
        :close-icon="false"
        :esc-close="false"
        :value="modelValue"
        :width="1200"
        :auto-close="false"
        @value-change="handleValueChange"
        @confirm="handleConfirm">
        <Selector :key="selectorKey" @change="handleIpSelectorChange"></Selector>
    </bcs-dialog>
</template>
<script lang="ts">
    import { defineComponent, ref, toRefs, watch } from '@vue/composition-api'
    import Selector from './ip-selector-bcs.vue'

    export default defineComponent({
        name: 'selector-dialog',
        components: {
            Selector
        },
        model: {
            prop: 'modelValue',
            event: 'change'
        },
        props: {
            modelValue: {
                type: Boolean,
                default: false
            }
        },
        setup (props, ctx) {
            const { emit } = ctx
            const ipList = ref([])

            const { modelValue } = toRefs(props)
            const selectorKey = ref(String(new Date().getTime()))
            watch(modelValue, () => {
                selectorKey.value = String(new Date().getTime())
            })
            const handleValueChange = (value: boolean) => {
                emit('change', value)
            }

            const handleIpSelectorChange = (data) => {
                ipList.value = data
            }

            const handleConfirm = () => {
                if (!ipList.value.length) {
                    ctx.root.$bkMessage({
                        theme: 'error',
                        message: ctx.root.$i18n.t('请选择服务器')
                    })
                    return
                }
                emit('confirm', ipList.value)
            }

            return {
                selectorKey,
                handleValueChange,
                handleConfirm,
                handleIpSelectorChange
            }
        }
    })
</script>
<style lang="postcss" scoped>
.selector-dialog {
    >>> .bk-dialog {
        top: 100px;
    }
    >>> .bk-dialog-tool {
        display: none;
    }
    >>> .bk-dialog-body {
        padding: 0;
    }
    >>> .bk-dialog-footer {
        border-top: none;
    }
}
</style>
