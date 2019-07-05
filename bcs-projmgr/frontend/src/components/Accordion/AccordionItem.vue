<template>
    <div class='devops-accordion-item'>
        <header @click='toggleContent' class='devops-accordion-item-header'>
            <i :class='{"bk-icon": true, "icon-angle-down": true, "open": isContentShow}'></i>
            <slot name='header'></slot>
        </header>
        <div v-show='isContentShow' class='devops-accordion-item-content'>
            <slot name='content'></slot>
        </div>
    </div>
</template>


<script lang="ts">
    import Vue from 'vue'
    import { Component, Prop, Watch } from 'vue-property-decorator'
    
    @Component
    export default class AccordionItem extends Vue {
        @Prop({ default: false })
        initContentShow

        isContentShow: boolean = this.initContentShow
        
        @Watch ('initContentShow')
        updateIsContentShow (val: boolean): void {
            this.isContentShow = val
        }

        toggleContent () {
            this.isContentShow = !this.isContentShow
            this.$emit('update:contentShow', this.isContentShow)
        }
    }
</script>

<style lang="scss">
    @import '../../assets/scss/conf';
    $titleHeight: 46px;
    .devops-accordion-item {
        &-header {
            display: flex;
            align-items: center;
            height: $titleHeight;
            line-height: $titleHeight;
            font-size: 16px;
            font-weight: normal;
            color: $fontWeightColor;
            position: relative;
            background: $bgHoverColor;
            cursor: pointer;
            border-top: 1px solid $borderWeightColor;
            box-shadow: 0 1px 0 $borderWeightColor;

            > .icon-angle-down {
                display: block;
                font-size: 11px;
                width: 40px;
                text-align: center;
                height: $titleHeight;
                line-height: $titleHeight;
                transform: rotate(-90deg);
                transition: all 0.3s ease;
                &.open {
                    transform: rotate(0deg)
                }
            }
        }

        &-content {
            display: flex;
        }
    }
</style>