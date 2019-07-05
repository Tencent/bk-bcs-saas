<template>
    <div class="biz-page-count">
        <div class="total-page">
            共计{{total || totalPage}}条
        </div>
        <div class="page-count-selector">
            每页
            <bk-selector
                style="width: 70px; display: inline-block;"
                :placeholder="'请选择要实例化的模板'"
                :selected.sync="selected"
                :list="pageCounterList"
                @item-selected="pageCounterSelect">
            </bk-selector>
            条
        </div>
    </div>
</template>

<script>
    export default {
        props: {
            totalPage: {
                type: Number,
                default: 0
            },
            total: {
                type: Number,
                default: 0
            },
            pageSize: {
                type: Number,
                default: 10
            }
        },
        data () {
            return {
                selected: this.pageSize,
                pageCounterList: [
                    {
                        id: 5,
                        name: '5'
                    },
                    {
                        id: 10,
                        name: '10'
                    },
                    {
                        id: 20,
                        name: '20'
                    },
                    {
                        id: 50,
                        name: '50'
                    },
                    {
                        id: 100,
                        name: '100'
                    }
                ]
            }
        },
        methods: {
            pageCounterSelect (data) {
                this.$emit('change', data)
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
