<template>
    <bk-sideslider
        :is-show.sync="visibility"
        :title="'如何推送Helm Chart到项目仓库'"
        :width="900"
        :quick-close="true">
        <div slot="content">
            <div v-html="markdown" class="biz-markdown-content" id="markdown"></div>
        </div>
    </bk-sideslider>
</template>

<script>
    import MarkdownIt from 'markdown-it'

    export default {
        props: {
            isShow: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                visibility: this.isShow,
                markdown: ''
            }
        },
        mounted () {
            this.init()
        },
        methods: {
            /**
             * 显示
             */
            show () {
                this.visibility = true
                this.$emit('status-change', this.visibility)
            },

            /**
             * 隐藏
             */
            hide () {
                this.visibility = false
                this.$emit('status-change', this.visibility)
            },

            /**
             * 初始化
             */
            async init () {
                const projectId = this.$route.params.projectId
                const markdown = await this.$store.dispatch('helm/getQuestionsMD', projectId)
                const md = new MarkdownIt({
                    linkify: false
                })
                this.markdown = md.render(markdown)
                this.$nextTick(() => {
                    // 让markdown文档里的标签新开窗口打开
                    const markdownDom = document.getElementById('markdown')
                    markdownDom.querySelectorAll('a').forEach(item => {
                        item.target = '_blank'
                    })
                })
            }
        }
    }
</script>
