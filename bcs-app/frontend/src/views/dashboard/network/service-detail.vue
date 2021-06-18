<template>
    <div class="detail p30">
        <div class="detail-title">
            {{ $t('基础信息') }}
        </div>
        <div class="detail-content basic-info">
            <div class="basic-info-item selector">
                <p class="mb10">{{ $t('选择器') }}:</p>
                <p class="bcs-ellipsis" v-bk-tooltips="transformObjToStr(data.spec.selector)">
                    {{ transformObjToStr(data.spec.selector) }}
                </p>
            </div>

            <div class="basic-info-item">
                <p class="mb10">{{ $t('类型') }}:</p>
                <p class="bcs-ellipsis">{{ data.spec.type }}</p>
            </div>
            <div class="basic-info-item">
                <p class="mb10">{{ $t('Service IP') }}:</p>
                <p class="bcs-ellipsis"></p>
            </div>
            <div class="basic-info-item">
                <p class="mb10">{{ $t('Service Domain') }}:</p>
                <p class="bcs-ellipsis"></p>
            </div>
        </div>
    </div>
</template>
<script lang="ts">
    import { defineComponent } from '@vue/composition-api'

    export default defineComponent({
        name: 'ServiceDetail',
        props: {
            // 当前行数据
            data: {
                type: Object,
                default: () => ({})
            }
        },
        setup () {
            const transformObjToStr = (obj) => {
                if (!obj) return '--'

                return Object.keys(obj).reduce((pre, key) => {
                    pre += `${key}=${obj[key]}`
                    return pre
                }, '')
            }

            return {
                transformObjToStr
            }
        }
    })
</script>
<style lang="postcss" scoped>
.detail {
    &-title {
        margin-bottom: 10px;
        font-size: 14px;
        color: #333948;
    }
    &-content {
        &.basic-info {
            display: flex;
            justify-content: space-between;
            border: 1px solid #dfe0e5;
            border-radius: 2px;
            margin-bottom: 25px;
            .basic-info-item {
                flex: 1;
                padding: 15px;
                height: 78px;
                font-size: 14px;
                color: #737987;
                border-right: 1px solid #dfe0e5;
                &.selector {
                    flex: 1.5;
                }
                &:last-child {
                    border-right: none;
                }
            }
        }
    }
}
</style>
