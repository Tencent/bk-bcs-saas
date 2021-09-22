<template>
    <bcs-form :label-width="100">
        <bcs-form-item :label="$t('版本')" required>
            <bcs-select></bcs-select>
        </bcs-form-item>
        <bcs-form-item :label="$t('网络类型')">
            <bcs-select></bcs-select>
        </bcs-form-item>
        <bcs-form-item :label="$t('所属区域')">
            <bcs-select></bcs-select>
        </bcs-form-item>
        <bcs-form-item :label="$t('所属VPC')" required>
            <bcs-select></bcs-select>
        </bcs-form-item>
        <bcs-form-item :label="$t('容器网络')" required>

        </bcs-form-item>
    </bcs-form>
</template>
<script lang="ts">
    import { defineComponent } from '@vue/composition-api'

    export default defineComponent({
        name: 'FormMode',
        setup (props, ctx) {

        }
    })
</script>
<style lang="postcss" scoped>

</style>
