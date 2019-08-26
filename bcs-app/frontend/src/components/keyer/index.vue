<template>
    <div class="bk-keyer">
        <div class="biz-keys-list mb10">
            <div class="biz-key-item" v-for="(keyItem, index) in list" :key="index">
                <template v-if="varList.length">
                    <bk-input
                        type="text"
                        :placeholder="keyPlaceholder"
                        style="width: 240px;"
                        :value.sync="keyItem.key"
                        :list="varList"
                        :disabled="keyItem.disabled && !keyItem.linkMessage"
                        @input="valueChange"
                        @paste="pasteKey(keyItem, $event)">
                    </bk-input>
                </template>
                <template v-else>
                    <input
                        type="text"
                        class="bk-form-input"
                        :placeholder="keyPlaceholder"
                        v-model="keyItem.key"
                        :disabled="keyItem.disabled && !keyItem.linkMessage"
                        @paste="pasteKey(keyItem, $event)"
                        @input="valueChange"
                    />
                </template>

                <span class="operator">=</span>

                <template v-if="varList.length">
                    <bk-input
                        type="text"
                        :placeholder="valuePlaceholder"
                        style="width: 240px;"
                        :value.sync="keyItem.value"
                        :list="varList"
                        :disabled="keyItem.disabled && !keyItem.linkMessage"
                        @input="valueChange"
                    >
                    </bk-input>
                </template>
                <template v-else>
                    <input
                        type="text"
                        class="bk-form-input"
                        :placeholder="valuePlaceholder"
                        v-model="keyItem.value"
                        @input="valueChange"
                        :disabled="keyItem.disabled && !keyItem.linkMessage"
                    />
                </template>

                <button class="action-btn" @click.stop.prevent="addKey">
                    <i class="bk-icon icon-plus"></i>
                </button>
                <button class="action-btn" v-if="list.length > 1" @click.stop.prevent="removeKey(keyItem, index)">
                    <i class="bk-icon icon-minus"></i>
                </button>
                <label class="bk-form-checkbox" style="margin-left: 20px;" v-if="isLinkToSelector">
                    <input type="checkbox" v-model="keyItem.isSelector" @change="valueChange">
                    {{addToSelectorStr}}
                </label>
                <div v-if="keyItem.linkMessage" class="biz-tip mt5 f12">{{keyItem.linkMessage}}</div>
            </div>
        </div>
        <slot>
            <p :class="['biz-tip', { 'is-danger': isTipChange }]">{{tip ? tip : '小提示：同时粘贴多行“键=值”的文本会自动添加多行记录'}}</p>
        </slot>
    </div>
</template>

<script>
    export default {
        props: {
            keyList: {
                type: Array,
                default: []
            },
            tip: {
                type: String,
                default: ''
            },
            isTipChange: {
                type: Boolean,
                default: false
            },
            isLinkToSelector: {
                type: Boolean,
                default: false
            },
            varList: {
                type: Array,
                default () {
                    return []
                }
            },
            keyPlaceholder: {
                type: String,
                default: '键'
            },
            valuePlaceholder: {
                type: String,
                default: '值'
            },
            addToSelectorStr: {
                type: String,
                default: '添加至选择器'
            }
        },
        data () {
            return {
                list: this.keyList
            }
        },
        watch: {
            'keyList' (val) {
                if (this.keyList && this.keyList.length) {
                    this.list = this.keyList
                } else {
                    this.list = [{
                        key: '',
                        value: ''
                    }]
                }
            }
        },
        methods: {
            addKey () {
                const params = {
                    key: '',
                    value: ''
                }
                if (this.isLinkToSelector) {
                    params.isSelector = false
                }
                this.list.push(params)
                const obj = this.getKeyObject(true)
                this.$emit('change', this.list, obj)
            },
            removeKey (item, index) {
                this.list.splice(index, 1)
                const obj = this.getKeyObject(true)
                this.$emit('change', this.list, obj)
            },
            valueChange () {
                const obj = this.getKeyObject(true)
                this.$emit('change', this.list, obj)
            },
            pasteKey (item, event) {
                const cache = item.key
                const clipboard = event.clipboardData
                const text = clipboard.getData('Text')

                if (text && text.indexOf('=') > -1) {
                    this.paste(event)
                    item.key = cache
                    setTimeout(() => {
                        item.key = cache
                    }, 0)
                }
            },
            paste (event) {
                const clipboard = event.clipboardData
                const text = clipboard.getData('Text')
                const items = text.split('\n')
                items.forEach(item => {
                    if (item.indexOf('=') > -1) {
                        const arr = item.split('=')
                        this.list.push({
                            key: arr[0],
                            value: arr[1]
                        })
                    }
                })
                setTimeout(() => {
                    this.formatData()
                }, 10)

                return false
            },
            formatData () {
                // 去掉空值
                if (this.list.length) {
                    const results = []
                    const keyObj = {}
                    const length = this.list.length
                    this.list.forEach((item, i) => {
                        if (item.key || item.value) {
                            if (!keyObj[item.key]) {
                                results.push(item)
                                keyObj[item.key] = true
                            }
                        }
                    })
                    const patchLength = results.length - length
                    if (patchLength > 0) {
                        for (let i = 0; i < patchLength; i++) {
                            results.push({
                                key: '',
                                value: ''
                            })
                        }
                    }
                    this.list.splice(0, this.list.length, ...results)
                    this.$emit('change', this.list)
                }
            },
            getKeyList (isAll) {
                let results = []
                const list = this.list
                if (isAll) {
                    return this.list
                } else {
                    results = list.filter(item => {
                        return item.key && item.value
                    })
                }

                return results
            },
            getKeyObject (isAll) {
                const results = this.getKeyList(isAll)
                if (results.length === 0) {
                    return {}
                } else {
                    const obj = {}
                    results.forEach(item => {
                        if (isAll) {
                            obj[item.key] = item.value
                        } else if (item.key && item.value) {
                            obj[item.key] = item.value
                        }
                    })
                    return obj
                }
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '../../css/variable.css';

    .biz-keys-list .action-btn {
        width: auto;
        padding: 0;
        margin-left: 5px;
        &.disabled {
            cursor: default;
            color: #ddd !important;
            border-color: #ddd !important;
            .bk-icon {
                color: #ddd !important;
                border-color: #ddd !important;
            }
        }
        &:hover {
            color: $primaryColor;
            border-color: $primaryColor;
            .bk-icon {
                color: $primaryColor;
                border-color: $primaryColor;
            }
        }
    }
    .is-danger {
        color: $dangerColor;
    }
</style>
