<template>
    <div class="bk-diff">
        <div v-html="html" v-highlight></div>
    </div>
</template>

<script>
    import { createPatch } from 'diff'
    import { Diff2Html } from 'diff2html'
    import hljs from 'highlight.js/lib/highlight'

    export default {
        name: 'bk-diff',
        directives: {
            highlight: el => {
                const hljsLanguageConfig = [
                    'javascript',
                    'json',
                    'shell',
                    'bash',
                    'xml',
                    'vim'
                ]

                hljsLanguageConfig.forEach(lang => {
                    import(
                        /* webpackChunkName: 'hljs' */
                        `highlight.js/lib/languages/${lang}`
                    ).then(langModule => {
                        hljs.registerLanguage(lang, langModule.default)
                    })
                })

                const blocks = el.querySelectorAll('code')

                blocks.forEach(block => {
                    hljs.highlightBlock(block)
                })
            }
        },
        props: {
            oldContent: {
                type: String,
                default: ''
            },
            newContent: {
                type: String,
                default: ''
            },
            context: {
                type: Number,
                default: 5
            },
            format: {
                type: String,
                default: 'line-by-line'
            }
        },
        computed: {
            html () {
                return this.createdHtml(this.oldContent, this.newContent, this.context, this.format)
            }
        },
        
        methods: {
            getDiffJson (oldContent, newContent, context, outputFormat) {
                const args = ['', oldContent, newContent, '', '', { context: context }]
                const patch = createPatch(...args)
                const outStr = Diff2Html.getJsonFromDiff(patch, {
                    inputFormat: 'diff',
                    outputFormat: outputFormat,
                    showFiles: true,
                    matching: 'lines'
                })
                
                const addLines = outStr[0].addedLines
                const deleteLines = outStr[0].deletedLines
                const changeLines = Math.max(addLines, deleteLines)
                outStr.changeLines = changeLines

                return outStr
            },
            createdHtml (oldContent, newContent, context, outputFormat) {
                function htmlReplace (html) {
                    return html.replace(
                        /<span class="d2h-code-line-ctn">(.+?)<\/span>/g,
                        '<span class="d2h-code-line-ctn"><code>$1</code></span>'
                    )
                }
                
                let diffJsonConf = this.getDiffJson(oldContent, newContent, context, outputFormat)

                // 没有改变时，强制出现对比
                if (!diffJsonConf.changeLines) {
                    diffJsonConf = this.getDiffJson(oldContent, newContent + '\r', context)
                }

                const html = Diff2Html.getPrettyHtml(diffJsonConf, {
                    inputFormat: 'json',
                    outputFormat: outputFormat,
                    showFiles: false,
                    matching: 'lines'
                })
                this.$emit('change-count', diffJsonConf.changeLines)
                return htmlReplace(html)
            }
        }
    }
</script>

<style>
    @import './diff.css';
</style>
