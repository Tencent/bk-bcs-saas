<template>
    <div class="bk-diff">
        <div v-html="html" v-highlight></div>
    </div>
</template>

<script>
    import { createPatch } from 'diff'
    import { Diff2Html } from 'diff2html'
    import hljs from 'highlight.js/lib/highlight'
    // 1. dynamic import 不支持通配符 https://github.com/rollup/rollup/issues/2097
    // 2. UMD and IIFE output formats are not supported for code-splitting builds https://github.com/rollup/rollup/issues/2072
    import java from 'highlight.js/lib/languages/java'
    import javascript from 'highlight.js/lib/languages/javascript'
    import json from 'highlight.js/lib/languages/json'
    import css from 'highlight.js/lib/languages/css'
    import scss from 'highlight.js/lib/languages/scss'
    import less from 'highlight.js/lib/languages/less'
    import stylus from 'highlight.js/lib/languages/stylus'
    import shell from 'highlight.js/lib/languages/shell'
    import bash from 'highlight.js/lib/languages/bash'
    import cpp from 'highlight.js/lib/languages/cpp'
    import go from 'highlight.js/lib/languages/go'
    import xml from 'highlight.js/lib/languages/xml'
    import python from 'highlight.js/lib/languages/python'
    import typescript from 'highlight.js/lib/languages/typescript'
    import sql from 'highlight.js/lib/languages/sql'
    import ruby from 'highlight.js/lib/languages/ruby'
    import ini from 'highlight.js/lib/languages/ini'
    import vim from 'highlight.js/lib/languages/vim'
    import php from 'highlight.js/lib/languages/php'
    import makefile from 'highlight.js/lib/languages/makefile'
    import lua from 'highlight.js/lib/languages/lua'

    function registerLanguage (lang, langModule) {
        hljs.registerLanguage(lang, langModule)
    }

    export default {
        name: 'bk-diff',
        directives: {
            highlight: el => {
                [
                    { lang: 'java', mod: java }, { lang: 'javascript', mod: javascript }, { lang: 'json', mod: json },
                    { lang: 'css', mod: css }, { lang: 'scss', mod: scss }, { lang: 'less', mod: less },
                    { lang: 'stylus', mod: stylus }, { lang: 'shell', mod: shell }, { lang: 'bash', mod: bash },
                    { lang: 'cpp', mod: cpp }, { lang: 'go', mod: go }, { lang: 'xml', mod: xml },
                    { lang: 'python', mod: python }, { lang: 'typescript', mod: typescript }, { lang: 'sql', mod: sql },
                    { lang: 'ruby', mod: ruby }, { lang: 'ini', mod: ini }, { lang: 'vim', mod: vim },
                    { lang: 'php', mod: php }, { lang: 'makefile', mod: makefile }, { lang: 'lua', mod: lua }
                ].forEach(item => {
                    registerLanguage(item.lang, item.mod)
                })

                // hljsLanguageConfig.forEach(lang => {
                //     import(
                //         /* webpackChunkName: 'hljs' */
                //         `highlight.js/lib/languages/${lang}`
                //     ).then(langModule => {
                //         hljs.registerLanguage(lang, langModule.default)
                //     })
                // })

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
            createdHtml (oldContent, newContent, context, outputFormat) {
                function htmlReplace (html) {
                    return html.replace(
                        /<span class="d2h-code-line-ctn">(.+?)<\/span>/g,
                        '<span class="d2h-code-line-ctn"><code>$1</code></span>'
                    )
                }
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
                const html = Diff2Html.getPrettyHtml(outStr, {
                    inputFormat: 'json',
                    outputFormat: outputFormat,
                    showFiles: false,
                    matching: 'lines'
                })
                this.$emit('change-count', Math.max(addLines, deleteLines))
                return htmlReplace(html)
            }
        }
    }
</script>

<style>
    @import './diff.css';
</style>
