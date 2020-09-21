/**
 * @file ee main entry
 */

import Vue from 'vue'
import VeeValidate from 'vee-validate'
import VueI18n from 'vue-i18n'

import bkMagic from '@open/components/bk-magic/bk-magic-vue.min'
import '@open/common/bkmagic'
import { bus } from '@open/common/bus'
import { loadScript } from '@open/common/util'
import appHeader from '@open/components/app-header.vue'
import Exception from '@open/components/exception'
import bkSelector from '@open/components/selector'
import bkDataSearcher from '@open/components/data-searcher'
import bkPageCounter from '@open/components/page-counter'
import bkNumber from '@open/components/number'
import bkInput from '@open/components/bk-input'
import bkCombox from '@open/components/bk-input/combox'
import bkTextarea from '@open/components/bk-textarea'
import { injectCSRFTokenToHeaders } from '@open/api'
import focus from '@open/directives/focus/index'

import App from './App'
import router from './router'
import store from './store'
import PROJECT_CONFIG from './config'
import AuthComponent from './components/auth'
import ApplyPerm from './components/apply-perm'
import bkGuide from './components/guide'
import bkFileUpload from './components/file-upload'
import k8sIngress from './views/ingress/k8s-ingress.vue'

import lang from './common/lang'

if (NODE_ENV === 'development') {
    Vue.config.devtools = true
}

Vue.component('app-header', appHeader)
Vue.component('app-exception', Exception)
Vue.component('app-auth', AuthComponent)
Vue.component('app-apply-perm', ApplyPerm)
Vue.component('bk-number-input', bkNumber)
Vue.component('bk-input', bkInput)
Vue.component('bk-combox', bkCombox)
Vue.component('bk-textarea', bkTextarea)
Vue.component('bk-file-upload', bkFileUpload)
Vue.component('bk-selector', bkSelector)
Vue.component('bk-guide', bkGuide)
Vue.component('bk-data-searcher', bkDataSearcher)
Vue.component('bk-page-counter', bkPageCounter)
Vue.component('k8s-ingress', k8sIngress)

Vue.use(VueI18n)
Vue.use(VeeValidate)
Vue.use(focus)

/**
 * 加载 devops-utils.js 的回调函数
 *
 * @param {string} e 错误信息
 */
function loadScriptCallback (e) {
    if (e) {
        console.error(e)
        return
    }

    injectCSRFTokenToHeaders()

    Vue.mixin({
        data () {
            return { PROJECT_CONFIG }
        }
    })

    const en = {}
    const cn = {}
    Object.keys(lang).forEach(key => {
        en[key] = lang[key][0]
        cn[key] = lang[key][1] || key
    })

    const messages = {
        'en-US': Object.assign(bkMagic.langPkg.enUS, en),
        'zh-CN': Object.assign(bkMagic.langPkg.zhCN, cn)
    }

    // 代码中获取当前语言 this.$i18n.locale
    const i18n = new VueI18n({
        locale: store.getters.lang,
        fallbackLocale: 'zh-CN',
        // silentTranslationWarn: true,
        messages
    })

    bkMagic.locale.i18n((key, value) => i18n.t(key, value))

    if (store.getters.lang === 'en-US') {
        document.body.style.fontFamily = 'arial,sans-serif'
    }

    window.bus = bus
    window.mainComponent = new Vue({
        el: '#app',
        router,
        store,
        components: {
            App
        },
        i18n,
        template: '<App/>'
    })
}

loadScript(DEVOPS_HOST + '/console/static/devops-utils.js', loadScriptCallback)
// loadScriptCallback()
