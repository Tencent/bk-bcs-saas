<template>
    <bk-dialog
        class='devops-announcement-dialog'
        :is-show.sync='showDialog'
        :width='828'
        :padding='0'
        :has-footer='false'
        :has-header='false'
        :close-icon='false'
        :quick-close='false'>
        <main slot='content' class='new-service-content' v-show='renderObj.id'>
            <div class="announcement-title">
                <i class="bk-icon icon-close" @click='closeDialog()'></i>
                <h2>{{ renderObj.noticeTitle }}</h2>
            </div>
            <div class="announcement-content">
                <div class="content-detail" v-html='renderObj.noticeContent'></div>
            </div>
            <div class="announcement-footer">
                <bk-button type='primary' @click='toLink(renderObj.redirectUrl)'>立即体验</bk-button>
            </div>
        </main>
    </bk-dialog>
</template>

<script lang='ts'>
    import Vue from 'vue'
    import { Component, Prop, Watch } from 'vue-property-decorator'
    import { State, Action, Getter } from 'vuex-class'

    @Component
    export default class NewServiceDialog extends Vue {
        @Action getAnnouncement

        showDialog: boolean = false
        renderObj: object = {}

        get announcementHistory () : object[] {
            const announcementHistory = localStorage.getItem('announcementHistory')
            return announcementHistory ? JSON.parse(announcementHistory) : []
        }

        mounted () {
            this.init()
        }

        async init () {
            try {
                const res = await this.getAnnouncement()

                if (res && this.announcementHistory.indexOf(res.id) === -1) {
                    this.announcementHistory.push(res.id)
                    localStorage.setItem('announcementHistory', JSON.stringify(this.announcementHistory))
                    Object.assign(this.renderObj, res)
                    this.showDialog = true
                }
            } catch (e) {
                this.$bkMessage({
                    message: e.message,
                    theme: 'error'
                })
            }
        }

        toLink (url) {
            if (url) {
                window.location.href = url
            } else {
                this.showDialog = false
            }
        }

        closeDialog () {
            this.showDialog = false
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../assets/scss/conf';

    .devops-announcement-dialog {
        .new-service-content {
            padding: 20px;
            height: 547px;
            background-image: url('../../assets/images/guide-foot.png');
            background-size: 100% 100%;
        }
        .announcement-title {
            text-align: center;
            color: $primaryColor;
            h2 {
                margin-top: 20px;
                font-size: 31px;
            }
            .icon-close {
                position: absolute;
                top: 20px;
                right: 16px;
                font-size: 16px;
                color: $fontWeightColor;
                cursor: pointer;
            }
        }
        .announcement-content {
            padding: 24px 50px 10px;
            height: 360px;
        }
        .announcement-footer {
            padding: 20px 0;
            text-align: center;
            .bk-button {
                padding: 0 50px;
                height: 46px;
                font-size: 20px;
            }
        }
    }
</style>
