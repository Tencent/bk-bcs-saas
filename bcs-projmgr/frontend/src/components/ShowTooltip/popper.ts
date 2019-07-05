
/*
 * Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
 * Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * http://opensource.org/licenses/MIT
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 *
 */

import Popper, { PopperOptions } from 'popper.js/dist/esm/popper.js'
import Vue from 'vue'
import { Component, Prop, Watch } from 'vue-property-decorator'

@Component
export default class Poppers extends Vue{
    @Prop({ default: 'bottom' })
    placement: string

    @Prop()
    reference: object

    @Prop()
    popper: object

    @Prop({ default: 0 })
    offset: number

    @Prop({ default: '' })
    transition: string

    @Prop({ default: false })
    value: boolean

    @Prop({
        default: {
            gpuAcceleration: false,
            boundariesElement: 'body'
        }
    })

    options: PopperOptions
    visible: boolean = this.value
    popperJS: Popper

    @Watch('value')
    handleValue (value, oldVal) {
        this.visible = value
        this.$emit('input', value)
    }

    @Watch('visible')
    handleVisible (visible, oldVal) {
        if (visible) {
            this.updatePopper()
            this.$emit('on-show', this)
        } else {
            this.destroyPopper()
            this.$emit('on-hide', this)
        }
        this.$emit('input', visible)
    }

    createPopper () {
        if (!/^(top|bottom|left|right)(-start|-end)?$/g.test(this.placement)) {
            return
        }

        const options = this.options
        const popper = this.popper || this.$refs.popper
        const reference = this.reference || this.$refs.reference

        if (!popper || !reference) {
            return
        }

        if (this.popperJS && this.popperJS.hasOwnProperty('destroy')) {
            this.popperJS.destroy()
        }

        options.placement = this.placement
        options.offset = this.offset

        this.popperJS = new Popper(reference, popper, Object.assign({}, options, {
            onCreate: popper => {
                this.resetTransformOrigin(popper.instance.popper)
                this.$nextTick(this.updatePopper)
                this.$emit('created', this)
            }
        }))
    }

    updatePopper () {
        this.popperJS ? this.popperJS.update() : this.createPopper()
    }

    doDestroy () {
        if (this.visible) {
            return
        }
        this.popperJS.destroy()
        this.popperJS = null
    }

    destroyPopper () {
        if (this.popperJS) {
            this.resetTransformOrigin(this.popperJS.popper)
        }
    }

    resetTransformOrigin (popperNode) {
        let placementMap = {top: 'bottom', bottom: 'top', left: 'right', right: 'left'}
        let placement = popperNode.getAttribute('x-placement').split('-')[0]
        let origin = placementMap[placement]
        popperNode.style.transformOrigin = ['top', 'bottom'].indexOf(placement) > -1
            ? 'center ' + origin
            : origin + ' center'
    }

    beforeDestroy () {
        if (this.popperJS) {
            this.popperJS.destroy()
        }
    }

}

// export default {
//     props: {
//         placement: {
//             type: String,
//             default: 'bottom'
//         },
//         reference: Object,
//         popper: Object,
//         offset: {
//             default: 0
//         },
//         value: {
//             type: Boolean,
//             default: false
//         },
//         transition: String,
//         options: {
//             type: Object,
//             default () {
//                 return {
//                     gpuAcceleration: false,
//                     boundariesElement: 'body'
//                 }
//             }
//         }
//     },
//     data () {
//         return {
//             visible: this.value
//         }
//     },
//     watch: {
//         value: {
//             immediate: true,
//             handler (val) {
//                 this.visible = val
//                 this.$emit('input', val)
//             }
//         },
//         visible (val) {
//             if (val) {
//                 this.updatePopper()
//                 this.$emit('on-show', this)
//             } else {
//                 this.destroyPopper()
//                 this.$emit('on-hide', this)
//             }
//             this.$emit('input', val)
//         }
//     },
//     methods: {
//         createPopper () {
//             if (!/^(top|bottom|left|right)(-start|-end)?$/g.test(this.placement)) {
//                 return
//             }
//
//             const options = this.options
//             const popper = this.popper || this.$refs.popper
//             const reference = this.reference || this.$refs.reference
//
//             if (!popper || !reference) {
//                 return
//             }
//
//             if (this.popperJS && this.popperJS.hasOwnProperty('destroy')) {
//                 this.popperJS.destroy()
//             }
//
//             options.placement = this.placement
//             options.offset = this.offset
//
//             this.popperJS = new Popper(reference, popper, Object.assign({}, options, {
//                 onCreate: popper => {
//                     this.resetTransformOrigin(popper.instance.popper)
//                     this.$nextTick(this.updatePopper)
//                     this.$emit('created', this)
//                 }
//             }))
//         },
//         updatePopper () {
//             this.popperJS ? this.popperJS.update() : this.createPopper()
//         },
//         doDestroy () {
//             if (this.visible) {
//                 return
//             }
//             this.popperJS.destroy()
//             this.popperJS = null
//         },
//         destroyPopper () {
//             if (this.popperJS) {
//                 this.resetTransformOrigin(this.popperJS.popper)
//             }
//         },
//         resetTransformOrigin (popperNode) {
//             let placementMap = {top: 'bottom', bottom: 'top', left: 'right', right: 'left'}
//             let placement = popperNode.getAttribute('x-placement').split('-')[0]
//             let origin = placementMap[placement]
//             popperNode.style.transformOrigin = ['top', 'bottom'].indexOf(placement) > -1
//                 ? 'center ' + origin
//                 : origin + ' center'
//         }
//     },
//     beforeDestroy () {
//         if (this.popperJS) {
//             this.popperJS.destroy()
//         }
//     }
// }
