import { defineComponent } from '@vue/composition-api'
import DashboardTopActions from './dashboard-top-actions'
import useCommon from './use-common'
import './base-layout.css'

export default defineComponent({
    name: 'BaseLayout',
    props: {
        title: {
            type: String,
            default: '',
            required: true
        },
        // 父分类，eg: workloads、networks（注意复数）
        type: {
            type: String,
            default: '',
            required: true
        },
        // 子分类，eg: deployments、ingresses
        category: {
            type: String,
            default: '',
            required: true
        },
        // 轮询时类型，eg: Deployment、Ingress（注意首字母大写）
        kind: {
            type: String,
            default: '',
            required: true
        },
        // 是否显示命名空间（不展示的话不会发送获取命名空间列表的请求）
        showNameSpace: {
            type: Boolean,
            default: true
        }
    },
    setup (props, ctx) {
        return {
            ...useCommon(ctx, {
                type: props.type,
                kind: props.kind,
                category: props.category,
                showNameSpace: props.showNameSpace
            })
        }
    },
    render () {
        return (
            <div class="biz-content">
                <div class="biz-top-bar">
                    <div class="dashboard-top-title">
                        {this.title}
                    </div>
                    <DashboardTopActions />
                </div>
                <div class="biz-content-wrapper" v-bkloading={{ isLoading: this.isLoading }}>
                    <div class="search-wapper mb20">
                        {
                            this.showNameSpace
                                ? (
                                    <bcs-select
                                        loading={this.namespaceLoading}
                                        class="namespace-select"
                                        v-model={this.namespaceValue}
                                        searchable
                                        placeholder={this.$t('请选择命名空间')}>
                                        {
                                            this.namespaceList.map(option => (
                                                <bcs-option
                                                    key={option.metadata.name}
                                                    id={option.metadata.name}
                                                    name={option.metadata.name}>
                                                </bcs-option>
                                            ))
                                        }
                                    </bcs-select>
                                )
                                : null
                        }
                        <bk-input
                            class="search-input"
                            clearable
                            v-model={this.nameValue}
                            placeholder={this.$t('输入名称搜索')}>
                        </bk-input>
                    </div>
                    {
                        this.$scopedSlots.default && this.$scopedSlots.default({
                            isLoading: this.isLoading,
                            pageConf: this.pageConf,
                            data: this.data,
                            curPageData: this.curPageData,
                            handlePageChange: this.handlePageChange,
                            handlePageSizeChange: this.handlePageSizeChange,
                            handleGetExtData: this.handleGetExtData,
                            handleSortChange: this.handleSortChange,
                            gotoDetail: this.gotoDetail,
                            handleShowDetail: this.handleShowDetail
                        })
                    }
                </div>
                <bcs-sideslider
                    quick-close
                    isShow={this.showDetailPanel}
                    title={this.curDetailRow.data?.metadata?.name}
                    width={800}
                    {
                    ...{
                        on: {
                            'update:isShow': (show: boolean) => {
                                this.showDetailPanel = show
                            }
                        },
                        scopedSlots: {
                            content: () => (this.$scopedSlots.detail && this.$scopedSlots.detail({
                                ...this.curDetailRow
                            }))
                        }
                    }
                    }></bcs-sideslider>
            </div>
        )
    }
})
