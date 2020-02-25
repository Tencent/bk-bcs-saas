<template>
    <div class="biz-data-searcher">
        <template v-if="localScopeList.length">
            <template v-if="scopeDisabled">
                <button class="bk-button trigger-btn disabled" style="max-width: 200px;">
                    <span class="btn-text tc">{{curScope.name}}</span>
                </button>
            </template>
            <template v-else>
                <bk-dropdown-menu ref="dropdown" trigger="click" :align="'left'">
                    <button class="bk-button trigger-btn" slot="dropdown-trigger" style="width: 200px;">
                        <span class="btn-text">{{curScope.name}}</span><i class="bk-icon icon-angle-down"></i>
                    </button>
                    <ul class="bk-dropdown-list" slot="dropdown-content">
                        <li class="dropdown-item">
                            <a href="javascript:;" v-for="scopeItem of localScopeList" :title="scopeItem.name" :key="scopeItem.id" @click="handleSechScope(scopeItem)">{{scopeItem.name}}</a>
                        </li>
                    </ul>
                </bk-dropdown-menu>
            </template>
        </template>
        <div class="biz-search-input" style="width: 300px;">
            <input
                type="text"
                class="bk-form-input"
                :placeholder="placeholderRender"
                v-model="localKey"
                @keyup.enter="handleSearch" />
            <a href="javascript:void(0)" class="biz-search-btn" v-if="!localKey">
                <i class="bk-icon icon-search" style="color: #c3cdd7;"></i>
            </a>
            <a href="javascript:void(0)" class="biz-search-btn" v-else @click.stop.prevent="clearSearch">
                <i class="bk-icon icon-close-circle-shape"></i>
            </a>
        </div>
        <div class="biz-refresh-wrapper" v-if="widthRefresh">
            <bk-tooltip class="refresh" :content="$t('刷新')" :delay="500" placement="top">
                <button :class="['bk-button bk-default is-outline is-icon']" @click="handleRefresh">
                    <i class="bk-icon icon-refresh"></i>
                </button>
            </bk-tooltip>
        </div>
    </div>
</template>

<script>
    // import { bkDropdownMenu } from '@open/components/bk-magic'

    export default {
        components: {
            // bkDropdownMenu
        },
        props: {
            placeholder: {
                type: String,
                default: ''
            },
            searchKey: {
                type: String,
                default: ''
            },
            searchScope: {
                type: String,
                default: ''
            },
            widthRefresh: {
                type: Boolean,
                default: true
            },
            scopeList: {
                type: Array,
                default () {
                    return []
                }
            },
            scopeDisabled: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                isTriggerSearch: false,
                isRefresh: false,
                localKey: this.searchKey,
                localScopeList: [],
                curScope: {
                    id: '',
                    name: this.$t('全部集群')
                },
                placeholderRender: ''
            }
        },
        watch: {
            searchKey (val) {
                this.localKey = val
            },
            scopeList () {
                this.initLocalScopeList()
            },
            localKey (newVal, oldVal) {
                // 如果删除，为空时触发搜索
                if (oldVal && !newVal && !this.isRefresh) {
                    this.clearSearch()
                }
            }
        },
        created () {
            this.initLocalScopeList()
            this.placeholderRender = this.placeholder || this.$t('输入关键字，按Enter搜索')
        },
        methods: {
            handleSechScope (data) {
                this.curScope = data
                this.$refs.dropdown.hide()
                this.$emit('update:searchScope', this.curScope.id)
                this.handleSearch()
            },
            initLocalScopeList () {
                this.localScopeList = JSON.parse(JSON.stringify(this.scopeList))
                if (this.localScopeList.length) {
                    this.curScope = this.localScopeList[0]
                }
                this.$emit('update:searchScope', this.curScope.id)
            },
            handleSearch () {
                this.isTriggerSearch = true
                this.$emit('update:searchKey', this.localKey)
                this.$emit('search')
                this.isRefresh = false
            },
            handleRefresh () {
                this.localKey = ''
                this.isRefresh = true
                if (this.localScopeList.length) {
                    this.curScope = this.localScopeList[0]
                }
                this.$emit('update:searchScope', this.curScope.id)
                this.$emit('update:searchKey', this.localKey)
                this.$emit('refresh')
            },
            clearSearch () {
                this.localKey = ''
                if (this.isTriggerSearch) {
                    this.handleSearch()
                    this.isTriggerSearch = false
                }
            }
        }
    }
</script>

<style scoped lang="postcss">
    @import '../../css/mixins/clearfix.css';
    @import '../../css/mixins/ellipsis.css';
    .biz-data-searcher {
        @mixin clearfix;

        .biz-search-input {
            .bk-form-input {
                border-radius: 0 2px 2px 0;
            }
        }

        .bk-dropdown-menu {
            .dropdown-item {
                > a {
                    width: 100%;
                    cursor: pointer;
                    display: inline-block;
                    vertical-align: middle;
                    @mixin ellipsis 240px;
                }
            }
            .bk-button {
                border-radius: 2px 0 0 2px;
                border-right: none;
            }
            float: left;
        }
    }
    .trigger-btn {
        &.disabled {
            margin-right: -10px;
            cursor: default;
            background: #fafafa;
        }
    }
    .btn-text {
        width: 140px;
        text-align: left;
        display: inline-block;
        vertical-align: middle;
        @mixin ellipsis 150px;
    }
</style>
