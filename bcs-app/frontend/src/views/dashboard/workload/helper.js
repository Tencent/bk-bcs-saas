import { computed } from '@vue/composition-api'

async function getClusters (ctx, state) {
    const { $route, $store } = ctx.root
    const projectId = computed(() => $route.params.projectId)
    try {
        const res = await $store.dispatch('cluster/getClusterList', projectId.value)
        state.clusterList = res.data.results || []
        $store.commit('cluster/forceUpdateClusterList', state.clusterList)
    } catch (e) {
        console.error(e)
        // TODO: 这里先不弹错误信息，统一处理那里会弹，之后接口统一在 store 里捕捉异常
        // state.bkMessageInstance = ctx.root.$bkMessage({
        //     theme: 'error',
        //     message: e.message || e.data.msg || e.statusText
        // })
    }
}

async function fetchNamespaceList (ctx, state) {
    const { $route, $store } = ctx.root

    const projectId = computed(() => $route.params.projectId)
    const curClusterId = computed(() => $store.state.curClusterId).value

    try {
        state.namespaceLoading = true
        const res = await $store.dispatch('dashboard/getNamespaceList', {
            projectId: projectId.value,
            clusterId: curClusterId
        })
        const data = res.data.manifest || {}
        state.namespaceList.splice(0, state.namespaceList.length, ...(data.items || []))
    } catch (e) {
        console.error(e)
        // TODO: 这里先不弹错误信息，统一处理那里会弹，之后接口统一在 store 里捕捉异常
        // state.bkMessageInstance = ctx.root.$bkMessage({
        //     theme: 'error',
        //     message: e.message || e.data.msg || e.statusText
        // })
    } finally {
        state.namespaceLoading = false
    }
}

export const fetchListByCategory = async (ctx, state, callback) => {
    const { $route, $store } = ctx.root

    const projectId = computed(() => $route.params.projectId)
    let curClusterId = computed(() => $store.state.curClusterId).value

    try {
        state.isLoading = true
        if (!curClusterId) {
            if (!state.clusterList) {
                await getClusters(ctx, state)
            }
            curClusterId = (state.clusterList[0] || {}).cluster_id || ''
        }
        fetchNamespaceList(ctx, state)
        const res = await $store.dispatch('dashboard/getListByCategory', {
            projectId: projectId.value,
            clusterId: curClusterId,
            category: state.category
        })
        callback(res.data || {})
    } catch (e) {
        console.error(e)
        // TODO: 这里先不弹错误信息，统一处理那里会弹，之后接口统一在 store 里捕捉异常
        // state.bkMessageInstance = ctx.root.$bkMessage({
        //     theme: 'error',
        //     message: e.message || e.data.msg || e.statusText
        // })
    } finally {
        setTimeout(() => {
            state.isLoading = false
        }, 100)
    }
}

export const search = (state, page) => {
    const allData = state.renderData.manifest.items

    const searchName = (state.nameValue || '').trim()

    const searchNameRet = []
    if (!searchName) {
        searchNameRet.splice(0, 0, ...allData)
    } else {
        allData.forEach(item => {
            if (item.metadata.name.indexOf(searchName) > -1) {
                searchNameRet.push(item)
            }
        })
    }

    const ret = []
    if (state.namespaceValue) {
        searchNameRet.forEach(item => {
            if (item.metadata.namespace === state.namespaceValue) {
                ret.push(item)
            }
        })
    } else {
        ret.splice(0, 0, ...searchNameRet)
    }
    state.initPageConf(ret, page)
    state.curPageData = state.getDataByPage(ret)
}

export const subscribeList = async (ctx, state) => {
    const { $route, $store } = ctx.root

    const projectId = computed(() => $route.params.projectId)
    const curClusterId = computed(() => $store.state.curClusterId).value
    try {
        const res = await $store.dispatch('dashboard/subscribeList', {
            projectId: projectId.value,
            clusterId: curClusterId,
            data: state.subscribeParams
        })
        const data = res.data || { events: [], latest_rv: null }

        if (data.latest_rv) {
            state.subscribeParams.resource_version = data.latest_rv
        }

        if (!data.events || !data.events.length) {
            return
        }

        const renderData = Object.assign({}, state.renderData)
        const { manifest, manifestExt } = renderData
        console.error(123213, state)
        data.events.forEach(event => {
            const uid = event.uid
            const operate = event.operate.toLowerCase()
            if (operate === 'deleted') {
                const matchItemIndex = manifest.items.findIndex(item => item.metadata.uid === uid)
                if (matchItemIndex !== -1) {
                    manifest.items.splice(matchItemIndex, 1)
                }
                if (manifestExt[uid]) {
                    delete manifestExt[uid]
                }
            } else if (operate === 'added') {
                const extData = event.manifest_ext
                const images = extData.images || []
                const age = extData.age || ''
                const createTime = extData.createTime || ''
                event.manifest.extraFE = { images, age, createTime }

                if (state.category === 'pods') {
                    const status = extData.status
                    const readyCnt = extData.readyCnt
                    const restartCnt = extData.restartCnt
                    event.manifest.extraFE = { images, age, createTime, status, readyCnt, restartCnt }
                } else if (state.category === 'cronjobs') {
                    const active = extData.active
                    const lastSchedule = extData.lastSchedule
                    event.manifest.extraFE = { images, age, createTime, active, lastSchedule }
                } else if (state.category === 'jobs') {
                    const duration = extData.duration
                    event.manifest.extraFE = { images, age, createTime, duration }
                }

                manifest.items.push(event.manifest)
                manifestExt[uid] = Object.assign({}, event.manifest_ext)
            } else if (operate === 'modified') {
                let matchItem = manifest.items.find(item => item.metadata.uid === uid)
                if (matchItem) {
                    const extData = event.manifest_ext
                    const images = extData.images || []
                    const age = extData.age || ''
                    const createTime = extData.createTime || ''
                    event.manifest.extraFE = { images, age, createTime }

                    if (state.category === 'pods') {
                        const status = extData.status
                        const readyCnt = extData.readyCnt
                        const restartCnt = extData.restartCnt
                        event.manifest.extraFE = { images, age, createTime, status, readyCnt, restartCnt }
                    } else if (state.category === 'cronjobs') {
                        const active = extData.active
                        const lastSchedule = extData.lastSchedule
                        event.manifest.extraFE = { images, age, createTime, active, lastSchedule }
                    } else if (state.category === 'jobs') {
                        const duration = extData.duration
                        event.manifest.extraFE = { images, age, createTime, duration }
                    }

                    matchItem = JSON.parse(JSON.stringify(event.manifest))

                    const matchItemIndex = manifest.items.findIndex(item => item.metadata.uid === uid)
                    manifest.items[matchItemIndex] = Object.assign({}, matchItem)

                    manifestExt[uid] = Object.assign({}, event.manifest_ext)
                }
            }
        })
        state.renderData = Object.assign({}, renderData)

        search(state)

        // state.initPageConf(state.renderData.manifest.items)
        // state.curPageData = state.getDataByPage(state.renderData.manifest.items)
    } catch (e) {
        console.error(e)
        // TODO: 这里先不弹错误信息，统一处理那里会弹，之后接口统一在 store 里捕捉异常
        // state.bkMessageInstance = ctx.root.$bkMessage({
        //     theme: 'error',
        //     message: e.message || e.data.msg || e.statusText
        // })
    }
}

export const startLoop = function (ctx, state) {
    const id = state.subscribeTimerId++
    state.subscribeTimerStore[id] = true
    async function timerFn () {
        if (!state.subscribeTimerStore[id]) {
            return
        }
        await subscribeList(ctx, state)
        setTimeout(timerFn, 5000)
    }
    timerFn()
}

export const stopLoop = function (state) {
    state.subscribeTimerStore = JSON.parse(JSON.stringify({}))
}
