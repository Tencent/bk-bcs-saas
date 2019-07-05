<template>
    <bk-dialog
        class='devops-project-logo-dialog'
        :is-show.sync='showDialog'
        :width='width'
        :has-header="logoDialogConf.hasHeader"
        :quick-close="logoDialogConf.quickClose">
        <main slot='content' class='project-logo-content'>
            <div class="info-title">修改LOGO</div>
            <div class="upload-content">
                <div class="upload-box">
                    <img :src="selectedUrl" v-if="selectedUrl">
                </div>
                <div class="upload-btn">
                    <input type="file" name="file" class="inputfile" id="inputfile"
                        accept="image/png, image/jpeg"
                        @change="fileChange">
                    <label for="file"><i class="bk-icon icon-bk"></i>选择LOGO</label>
                    <p class='logo-desc'>只允许上传png、jpg</p>
                    <p class='logo-desc'>大小不超过2M</p>
                </div>
            </div>
        </main>
        <template slot="footer">
            <div class="bk-dialog-outer">
                <template v-if="isUploading">
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary disabled">
                        修改中...
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel disabled">
                        取消
                    </button>
                </template>
                <template v-else>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-confirm bk-btn-primary"
                        @click="toConfirmLogo">
                        确定
                    </button>
                    <button type="button" class="bk-dialog-btn bk-dialog-btn-cancel" @click="toCloseDialog">
                        取消
                    </button>
                </template>
            </div>
        </template>
    </bk-dialog>
</template>

<script lang='ts'>
    import Vue from 'vue'
    import { Component, Prop, Watch } from 'vue-property-decorator'
    import { State, Action, Getter } from 'vuex-class'

    @Component
    export default class projectLogoDialog extends Vue {
        @Prop({ default: false })
        showDialog: boolean

        @Prop({ default: false })
        isUploading: boolean

        @Prop({ default: '' })
        selectedUrl: string

        @Prop()
        toConfirmLogo

        @Prop()
        toCloseDialog

        @Prop()
        fileChange

        width: number = 640
        curImage: string = ''

        get logoDialogConf (): object {
            return {
                hasHeader: false,
                quickClose: false
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../assets/scss/conf.scss';

    .devops-project-logo-dialog {
        .project-logo-content {
            .info-title {
                padding-top: 6px;
                padding-left: 10px;
                font-size: 22px;
                color: #333C48;
            }
        }
        .upload-content {
            display: flex;
            padding: 27px 10px;
        }
        .upload-box {
            margin-right: 16px;
            width: 128px;
            height: 128px;
            border: 1px solid $fontLigtherColor;
            background: $borderColor;
            &:before {
                content: '';
                position: absolute;
                width: 124px;
                height: 124px;
                background: #fff;
                border-radius: 50%;
                border: 1px dashed $fontLigtherColor;
            }
            img {
                position: relative;
                width: 126px;
                height: 126px;
                border-radius: 50%;
                z-index: 99;
            }
        }
        .upload-btn {
            color: $fontWeightColor;
            .logo-desc {
                line-height: 24px;
                font-size: 12px;
                color: $fontLigtherColor;
            }
        }
        .inputfile {
            width: 120px;
            height: 36px;
            opacity: 0;
            overflow: hidden;
            position: absolute;
            cursor: pointer;
        }
        .inputfile + label {
            margin-bottom: 10px;
            width: 120px;
            height: 36px;
            line-height: 36px;
            display: inline-block;
            text-align: center;
            background-color: $primaryColor;
            color: white;
            border-radius: 2px;
            .icon-bk {
                position: relative;
                top: 2px;
                margin-right: 4px;
                font-size: 16px;
            }
        }
        button.disabled {
            background-color: #fafafa;
            border-color: #e6e6e6;
            color: #ccc;
            cursor: not-allowed;
            &:hover {
                background-color: #fafafa;
                border-color: #e6e6e6;
            }
        }
    }
</style>
