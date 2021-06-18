/**
 * @file depot all
 * @author hieiwang <hieiwang@tencent.com>
 */

import moment from 'moment'
import faker from 'faker'
import chalk from 'chalk'

import {randomInt, sleep} from '../util'

export async function response(getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    console.log()
    const invoke = getArgs.invoke
    if (invoke === 'getImageLibrary') {
        const COUNT = randomInt(10, 20)
        const results = []
        for (let i = 0; i < COUNT; i++) {
            results.push({
                name: `paas/public/docker-builder${i}`,
                repo: 'paas/public/docker-builder',
                deployBy: 'system',
                type: 'public',
                desc: '',
                repoType: '',
                hasCollected: true,
                allCollectNum: 1
            })
        }
        return {
            code: 0,
            message: 'success',
            data: {
                count: COUNT,
                next: null,
                previous: null,
                results: results
            }
        }
    }
    return {
        code: 0,
        data: {}
    }
}

