import { reactive } from '@vue/composition-api'

export default params => {
    const pageConf = reactive(Object.assign({}, {
        total: 0,
        totalPage: 1,
        pageSize: 10,
        curPage: 1
    }, params))

    const initPageConf = (dataList, page) => {
        if (page) {
            pageConf.curPage = page
        }
        const total = dataList.length
        pageConf.total = total
        pageConf.totalPage = Math.ceil(total / pageConf.pageSize)
    }

    const getDataByPage = (dataList, page = pageConf.curPage) => {
        let startIndex = (page - 1) * pageConf.pageSize
        let endIndex = page * pageConf.pageSize
        if (startIndex < 0) {
            startIndex = 0
        }
        if (endIndex > dataList.length) {
            endIndex = dataList.length
        }
        return dataList.slice(startIndex, endIndex)
    }

    const pageChange = (dataList, page = 1) => {
        pageConf.curPage = page
        return getDataByPage(dataList, page)
    }

    const pageSizeChange = (dataList, pageSize) => {
        pageConf.pageSize = pageSize
        initPageConf(dataList, 1)
        return pageChange(dataList)
    }

    return {
        pageConf,
        initPageConf,
        getDataByPage,
        pageChange,
        pageSizeChange
    }
}
