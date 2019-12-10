/**
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import Vue from 'vue'
import VeeValidate from 'vee-validate'
import VueI18n from 'vue-i18n'

import bkMagic from './components/bk-magic/bk-magic-vue.min'
import './common/bkmagic'
import App from './App'
import router from './router'
import store from './store'
import { injectCSRFTokenToHeaders } from './api'
import { loadScript } from './common/util'
import { bus } from './common/bus'
import appHeader from './components/app-header.vue'
import Exception from './components/exception'
import AuthComponent from './components/auth'
import ApplyPerm from './components/apply-perm'
import bkGuide from './components/guide'
import bkSelector from './components/selector'
import bkDataSearcher from '@open/components/data-searcher'
import bkPageCounter from '@open/components/page-counter'

import bkNumber from './components/number'
// TODO: 可用组件替换
import bkInput from './components/bk-input'
import bkTextarea from './components/bk-textarea'

import focus from './directives/focus/index'

import PROJECT_CONFIG from './config'

import lang from './common/lang'

Vue.component('app-header', appHeader)
Vue.component('app-exception', Exception)
Vue.component('app-auth', AuthComponent)
Vue.component('app-apply-perm', ApplyPerm)
Vue.component('bk-number-input', bkNumber)
Vue.component('bk-input', bkInput)
Vue.component('bk-textarea', bkTextarea)
Vue.component('bk-selector', bkSelector)
Vue.component('bk-guide', bkGuide)
Vue.component('bk-data-searcher', bkDataSearcher)
Vue.component('bk-page-counter', bkPageCounter)

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
