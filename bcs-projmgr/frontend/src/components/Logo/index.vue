<template>
    <svg :width='size' :height='size'>
        <use v-bind="{'xlink:href': `#${name}`}"></use>
    </svg>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Prop } from 'vue-property-decorator'
const svgs = require.context('../../assets/scss/logo', true, /\.svg$/)
const svgsArray = svgs
    .keys()
    .map((key: string) => svgs(key))
    .keys()

@Component
export default class SvgLogo extends Vue {
    @Prop()
    name
    @Prop({ default: 32 })
    size
}
</script>
