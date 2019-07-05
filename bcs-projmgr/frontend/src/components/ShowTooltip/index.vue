<template>
	<div class="show-tooltip" @mouseenter="handleShowPopper" @mouseleave="handleClosePopper">
        <div class="show-tooltip-rel" ref="reference">
            <slot></slot>
        </div>
        <transition name="fade">
            <div
                class="show-tooltip-popper"
                ref="popper"
                v-show="visible || (always && finishCompute)"
                :style="{'margin': `${margin}`}"
                @mouseenter="handleShowPopper"
                @mouseleave="handleClosePopper">
                <div class="show-tooltip-content">
                    <div class="show-tooltip-arrows"></div>
                    <div class="show-tooltip-inner" :style="{width: `${width}px`}">
                        <slot name="content">{{ content }}</slot>
                        <div class="show-tooltip-footer">
                            <slot name="footer"><span class="close-tooltip-btn" @click="confirmBtn">{{ footer }}</span></slot>
                        </div>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>

<script lang='ts'>
    import Vue from 'vue'
    import { Component, Prop, Watch } from 'vue-property-decorator'
    import { State, Action, Getter } from 'vuex-class'
	import{ mixins } from 'vue-class-component'
	import Popper from './popper.ts'

	const oneOf = (value, validList) => {
        for (let i = 0; i < validList.length; i++) {
            if (value === validList[i]) {
                return true
            }
        }
        return false
    }
    @Component
    export default class ShowTooltip extends mixins(Popper) {
		@Prop({
			default: 'bottom',
			validator (value) {
                return oneOf(
                    value,
                    [
                        'top', 'top-start', 'top-end', 'bottom', 'bottom-start', 'bottom-end',
                        'left', 'left-start', 'left-end', 'right', 'right-start', 'right-end'
                    ]
                )
            }
		})
        placement: string

		@Prop({ default: '' })
        content: string

		@Prop({ default: '知道了' })
        footer: string

		@Prop({ default: '0' })
        margin: string

		@Prop({ default: 230 })
        width: number

		@Prop({ default: false })
        always: boolean

		finishCompute: boolean = false

		mounted () {
            if (this.always) {
				setTimeout(() => {
					this.finishCompute = true
					this.updatePopper()
				}, 500)
            }
        }

		handleShowPopper (): void  {
			// this.visible = true
        }

        handleClosePopper (): void  {
			// this.visible = false
        }

		confirmBtn (): void {
			this.$emit('confirm')
		}

    }
</script>

<style lang="scss">
	.show-tooltip {
		display: inline-block;
		.show-tooltip-rel {
			display: inline-block;
			position: relative;
		}
		.show-tooltip-popper {
			display: block;
			visibility: visible;
			font-size: 12px;
			line-height: 1.5;
			position: absolute;
			z-index: 1060;
			&[x-placement^="top"] {
				padding: 5px 0 8px 0;
				.show-tooltip-arrows {
					margin-left: -4px;
					left: 50%;
					bottom: 5px;
					transform: rotate(225deg);
				}
			}
			&[x-placement^="right"] {
				padding: 0 5px 0 8px;
				.show-tooltip-arrows {
					margin-top: -5px;
					top: 50%;
					left: 5px;
					transform: rotate(315deg);
				}
			}
			&[x-placement^="bottom"] {
				padding: 8px 0 5px 0;
				.show-tooltip-arrows {
					margin-left: -4px;
					top: 5px;
					left: 50%;
				}
			}
			&[x-placement^="left"] {
				padding: 0 8px 0 5px;
				.show-tooltip-arrows {
					margin-top: -5px;
					top: 50%;
					right: 5px;
					transform: rotate(135deg);
				}
			}
			&[x-placement="top-start"] {
				.show-tooltip-arrows {
					left: 10%;
				}
			}
			&[x-placement="top-end"] {
				.show-tooltip-arrows {
					left: 90%;
				}
			}
			&[x-placement="right-start"] {
				.show-tooltip-arrows {
					top: 30%;
				}
			}
			&[x-placement="right-end"] {
				.show-tooltip-arrows {
					top: 70%;
				}
			}
			&[x-placement="left-start"] {
				.show-tooltip-arrows {
					top: 30%;
				}
			}
			&[x-placement="left-end"] {
				.show-tooltip-arrows {
					top: 70%;
				}
			}
			&[x-placement="bottom-start"] {
				.show-tooltip-arrows {
					left: 10%;
				}
			}
			&[x-placement="bottom-end"] {
				.show-tooltip-arrows {
					left: 90%;
				}
			}
		}
		.show-tooltip-inner {
			max-width: 500px;
			min-height: 34px;
			padding: 16px 18px;
			color: #63656E;
			text-align: left;
			text-decoration: none;
			background-color: #fff;
			border-radius: 2px;
			white-space: normal;
			border:1px solid rgba(220,222,229,1);
			box-shadow:0px 2px 8px rgba(0,0,0,0.1);
			cursor: default;
		}
		.show-tooltip-footer {
			margin-top: 10px;
			text-align: right;
			color: #3A84FF;
		}
		.close-tooltip-btn {
			cursor: pointer;
		}
		.show-tooltip-arrows {
			padding-top: 4px;
			position: absolute;
			width: 8px;
			height: 8px;
			border: 1px solid #dcdee5;
			border-right-color: transparent;
			border-bottom-color: transparent;
			background-color: #fff;
			transform: rotate(45deg);
		}
	}
</style>
