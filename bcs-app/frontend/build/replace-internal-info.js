/**
 * @file 替换 asset js 中的敏感信息
 */

const fs = require('fs')
const path = require('path')
const stream = require('stream')
const fse = require('fs-extra')
const chalk = require('chalk')

console.log(chalk.cyan('  Start Replace...\n'))

const Transform = stream.Transform

// 打包的版本
const VERSION = process.env.VERSION

// 临时目录
const TMP_DIR = path.resolve(__dirname, '..', 'dist/js-tmp')

// 构建后的 js 目录
const DIST_DIR = path.resolve(__dirname, '..', 'dist', VERSION, 'static', 'js')
const distJSFiles = []
;(function walkTpl (filePath) {
    fs.readdirSync(filePath).forEach(item => {
        if (fs.statSync(filePath + '/' + item).isDirectory()) {
            walkTpl(filePath + '/' + item)
        } else {
            const ext = path.extname(item)
            if (ext === '.js') {
                distJSFiles.push({
                    fileName: item,
                    filePath: path.resolve(__dirname, '..', 'dist', filePath + '/' + item)
                })
            }
        }
    })
})(DIST_DIR)

const doTransform = file => {
    return new Promise((resolve, reject) => {
        const read = fs.createReadStream(file.filePath)
        read.setEncoding('utf-8').resume().pipe(
                fs.createWriteStream(
                    path.resolve(TMP_DIR, `${file.fileName}`)
                )
            ).on('finish', async () => {
                resolve(1)
            }).on('error', e => {
                console.error(e)
                reject(e)
            })
    })
}

fse.ensureDir(TMP_DIR, err => {
    if (err) {
        throw err
    }

    Promise.all(distJSFiles.map(async f => {
        await doTransform(f)
    })).then(async ret => {
        // await fse.copy(
        //     DIST_DIR,
        //     path.resolve(__dirname, '..', `dist/${VERSION}/static/js-origin`)
        // )
        await fse.move(
            TMP_DIR,
            DIST_DIR,
            { overwrite: true }
        )

        console.log(chalk.cyan('  Replace complete.\n'))
    })
})
