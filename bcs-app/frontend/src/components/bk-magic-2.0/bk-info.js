import Vue from 'vue'

const bkInfo = Vue.prototype.$bkInfo

const Info = function (opts = {}) {
    if (opts.content) {
        if (typeof opts.content === 'string') {
            opts.subTitle = opts.content
        }
        opts.subHeader = opts.content
    }

    if (opts.clsName) {
        opts.extCls = opts.clsName
    }

    opts.closeIcon = true
    opts.confirmLoading = true

    if (!opts.width) {
        opts.width = 360
    }
    bkInfo(opts)
}

Vue.prototype.$bkInfo = Info

export default Info
