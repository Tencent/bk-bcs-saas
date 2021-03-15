# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
# Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
import asyncio
import concurrent


class AsyncRunException(BaseException):
    pass


def async_run(tasks):
    """
    run a group of tasks async(仅适用于IO密集型)
    Requires the tasks arg to be a list of functools.partial()
    """

    # start a new async event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # https://github.com/python/asyncio/issues/258
    executor = concurrent.futures.ThreadPoolExecutor(8)
    loop.set_default_executor(executor)

    async_tasks = [asyncio.ensure_future(async_task(task, loop)) for task in tasks]
    # run tasks in parallel
    loop.run_until_complete(asyncio.wait(async_tasks))

    # deal with errors (exceptions, etc)
    err_msg_list = []
    for task in async_tasks:
        error = task.exception()
        if error is not None:
            err_msg_list.append(str(error))

    executor.shutdown(wait=True)

    if err_msg_list:
        raise AsyncRunException(';'.join(err_msg_list))


async def async_task(params, loop):
    """
    Perform a task asynchronously.
    """
    # get the calling function
    # This executes a task in its own thread (in parallel)
    await loop.run_in_executor(None, params)
