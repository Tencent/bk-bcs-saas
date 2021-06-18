/**
 * @file helm all
 */

import moment from 'moment'
import faker from 'faker'
import chalk from 'chalk'
import fs from 'fs'

import {randomInt, sleep} from '../util'

export async function response(getArgs, postArgs, req) {
    console.log(chalk.cyan('req', req.method))
    console.log(chalk.cyan('getArgs', JSON.stringify(getArgs, null, 0)))
    console.log(chalk.cyan('postArgs', JSON.stringify(postArgs, null, 0)))
    const invoke = getArgs.invoke

    if (invoke === 'checkAppStatus') {
        return {
            code: 0,
            data: {
                transitioning_action: 'rollback',
                transitioning_message: '',
                transitioning_on: true,
                transitioning_result: true
            },
            message: ''
        }
    }

    if (invoke === 'getAppInfo') {
        try {
            const jsonFile = `${__dirname}/../json/helm-app-status.json`
            return JSON.parse(fs.readFileSync(jsonFile))
        } catch (e) {
            return {
                code: 0,
                data: {}
            }
        }
    }

    return {
        code: 0,
        data: {}
    }
}

