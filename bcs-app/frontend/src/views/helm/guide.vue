<template>
    <bk-sideslider
        :is-show.sync="visibility"
        :title="$t('如何推送Helm Chart到项目仓库？')"
        :width="900"
        :quick-close="true">
        <div slot="content">
            <div v-html="markdown" class="biz-markdown-content" id="markdown"></div>
        </div>
    </bk-sideslider>
</template>

<script>
    import MarkdownIt from 'markdown-it'
    import Clipboard from 'clipboard'

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
                    markdownDom.querySelectorAll('pre').forEach(item => {
                        const btn = document.createElement('button')
                        const codeBox = document.createElement('div')
                        const code = item.querySelector('code').innerText
                        btn.className = 'bk-button bk-default bk-button-mini copy-btn'
                        codeBox.className = 'code-box'
                        btn.innerHTML = '<span><i class="bk-icon icon-clipboard mr5"></i>' + this.$t('复制') + '</span>'
                        btn.setAttribute('data-clipboard-text', code)
                        item.appendChild(btn)
                        codeBox.appendChild(item.querySelector('code'))
                        item.appendChild(codeBox)
                    })
                })

                if (this.clipboardInstance && this.clipboardInstance.off) {
                    this.clipboardInstance.off('success')
                }
                setTimeout(() => {
                    this.clipboardInstance = new Clipboard('.copy-btn')
                    console.log(this.clipboardInstance)
                    this.clipboardInstance.on('success', e => {
                        this.$bkMessage({
                            theme: 'success',
                            message: this.$t('复制成功')
                        })
                    })
                }, 2000)
            }
        }
    }
</script>

<style>
    .biz-markdown-content {
        pre {
            padding: 0;
            position: relative;

            code {
                word-break: break-all;
            }

            .code-box {
                padding: 10px;
                width: 100%;
                min-height: 30px;
                overflow: auto;
            }

            .copy-btn {
                display: none;
                position: absolute;
                right: 8px;
                top: 8px;
            }

            &:hover {
                .copy-btn {
                    display: inline-block;
                }
            }
        }
    }
</style>
