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
import logging
import time
import six

from celery import shared_task
from enum import Enum

logger = logging.getLogger(__name__)


class PollResultStatus(Enum):
    """一次轮询结果的状态"""
    SHOULD_RETRY = 1
    DOING = 2
    DONE = 3


PRS = PollResultStatus


class FinalState(Enum):
    """最终状态"""
    FINISHED = 0
    EXCEPTION = 1
    START_TIMEOUT = 2
    EXECUTE_TIMEOUT = 3
    MAX_RETRIES = 4

    @classmethod
    def exception_status(cls):
        return (
            cls.EXCEPTION,
            cls.START_TIMEOUT,
            cls.EXECUTE_TIMEOUT,
            cls.MAX_RETRIES
        )


def get_operations_map():
    """获取当前operation到poll_class的对应关系表
    """
    return PollerRegister.operation_map


class PollerRegister(type):
    operation_map = {}

    def __new__(cls, name, parents, attrs):
        new_cls = type.__new__(cls, name, parents, attrs)
        cls.operation_map[name] = new_cls  # registry
        return new_cls


class PollStatus(object):
    """每一次轮询到的任务状态"""

    def __init__(self, status, result, is_exception=False):
        """
        :param status: 表示这一次状态所代表的深层含义，如 DOING, SHOULD_RETRY, DONE
        :param result: 状态原始结果
        :param is_exception: 如果为True，表示该状态异常，并非真实状态
        """
        PRS(status)
        self.status = status
        self.result = result
        self._is_exception = is_exception

    def is_exception(self):
        return self._is_exception

    @classmethod
    def exception_result(cls):
        return cls(status=PRS.SHOULD_RETRY.value, result={}, is_exception=True)

    def __str__(self):
        return 'stauts=%s result=%s is_exception=%s' % (
            self.status, self.result, self.is_exception())


class PollResult(object):
    """状态轮询的最终结果"""

    def __init__(self, code, data=None, message=""):
        """
        :param code: 结果状态码
        :param data: 具体数据
        :param message: 提示信息
        """
        FinalState(code)
        self.code = code
        self.data = data if data is not None else {}
        self.message = message

    def is_exception(self):
        return FinalState(self.code) in FinalState.exception_status()

    def to_dict(self):
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data
        }

    def __str__(self):
        return '<%s: %s is_exception=%s>' % (
            self.__class__.__name__, self.to_dict(), self.is_exception())


class ResultHandlerRegister(type):
    handler_map = {}

    def __new__(cls, name, parents, attrs):
        new_cls = type.__new__(cls, name, parents, attrs)
        cls.handler_map[name] = new_cls  # registry
        return new_cls


class BaseResultHandler(six.with_metaclass(ResultHandlerRegister)):
    def __init__(self, params):
        """使用轮询参数初始化"""
        self.params = params

    def final_result_handler(self, poll_result):
        """处理最终结果
        :param poll_result: PollResult instance
        """
        raise NotImplementedError()


class BasePollerTaskStatus(six.with_metaclass(PollerRegister)):
    """Base class for task status poller"""

    max_retries = 10
    overall_timeout_seconds = 3600 * 24 * 7
    default_retry_delay_seconds = 10

    def __init__(self, params):
        self.params = params

    def get_timeout_result(self):
        return PollResult(
            code=FinalState.EXECUTE_TIMEOUT.value,
            message='Status query has exceeded total timeout, will not query anymore.'
        )

    def get_exception_result(self):
        return PollResult(
            code=FinalState.EXCEPTION.value,
            message='Exception when query status.'
        )

    def exceeded_max_retries(self):
        return PollResult(
            code=FinalState.MAX_RETRIES.value,
            message='poll status exceed max retries'
        )

    def get_retry_delay(self, queried_times, retries):
        """获取下一次任务应该被延迟的秒数"""
        return self.default_retry_delay_seconds

    # 查询状态
    def query_status(self):
        """用于单次查询任务执行状态"""
        raise NotImplementedError

    def safe_query_status(self):
        try:
            status_result = self.query_status()
        except Exception:
            # 出错时使用一个特殊的result来替代
            logger.exception(
                'Exception when query status, poll_class=%s' % self)
            status_result = PollStatus.exception_result()

        logger.debug('Query status result, poll_class=%s, Status result: %s' % (
            self, status_result))
        return status_result

    # 解析状态为结果
    def parse_status(self, status):
        """解析单次任务查询结果为PollResult"""
        raise NotImplementedError

    def safe_parse_status(self, status_result):
        """把单次查询结果PollStatus转换为PollResult
        :param status_result: PollStatus isinstance
        """
        if status_result.is_exception():
            return self.get_exception_result()
        else:
            try:
                return self.parse_status(status_result.result)
            except Exception:
                logger.exception(
                    'Exception when parse status, poll_class=%s' % self)
                return self.get_exception_result()

    def exceeded_timeout(self, ts_query_started):
        """检查状态轮询是否已经超时
        :param float ts_query_started: 第一次查询开始的时间戳
        """
        return (time.time() - ts_query_started) > self.overall_timeout_seconds

    def should_query_again(self, status_result, retries):
        """查询一次，该行为会影响should_query_again和retries
        :param status_result: PollStatus instance
        :param str retries: 当前重试次数
        :return bool
        """
        # 任务因为某种原因（异常等）需要重试，检查是否已经重试过太多次了
        if status_result.status == PRS.SHOULD_RETRY.value:
            if (retries + 1) > self.max_retries:
                return False, self.exceeded_max_retries()
            else:
                return True, None
        elif status_result.status == PRS.DOING.value:
            return True, None
        elif status_result.status == PRS.DONE.value:
            return False, PollResult(
                code=FinalState.FINISHED.value,
                data=status_result.result,
                message='finished'
            )

    def should_reset_retries(self, status_result):
        """是否应该重置重试次数
        :param status_result: PollStatus instance
        """
        return status_result.status == PRS.DOING.value

    def __str__(self):
        return '<%s: params=%s>' % (self.__class__.__name__, self.params)

    @classmethod
    def start(cls, params, result_handle_cls=None):
        result_handle_cls_signature = None
        if result_handle_cls is not None:
            assert issubclass(result_handle_cls, BaseResultHandler)
            result_handle_cls_signature = result_handle_cls.__name__

        check_status_until_finished.delay(
            cls.__name__, result_handle_cls_signature, params)


@shared_task(acks_late=True, name='poll_task.check_status_until_finished')
def check_status_until_finished(poller_name, result_handler_name, params, queue=None):
    """查询任务状态，如果出现查询异常或者正在进行，则派生一个子任务。
    否则直接返回任务结果
    :param str operation: 轮询操作类型
    :param params: 轮询参数
    :param poll_class: 用来处理轮询的class
    """
    retries = check_status_until_finished.request.retries
    ts_query_started = check_status_until_finished.request.get(
        'ts_query_started', time.time())
    request_headers = check_status_until_finished.request.headers or {}

    queried_times = request_headers.get('queried_times', 0)

    poll_class = get_operations_map()[poller_name]
    poller = poll_class(params)

    # 检查该任务轮询是否已经超时
    if poller.exceeded_timeout(ts_query_started=ts_query_started):
        logger.info('Status query for %s has exceeded total timeout, will not query anymore.'
                    'ts_query_started=%s' % (poller, ts_query_started))
        if result_handler_name is not None:
            result_handler_cls = ResultHandlerRegister.handler_map[result_handler_name]
            result_handler_cls(params).final_result_handler(
                poller.get_timeout_result())
        return

    status_result = poller.safe_query_status()
    # 检查是否应该过一段时间后重新查询
    should_retry, poll_result = poller.should_query_again(
        status_result, retries)
    if should_retry:
        countdown = poller.get_retry_delay(queried_times, retries)
        # 判断是否需要重置重试次数
        retries = 0 if poller.should_reset_retries(
            status_result) else retries + 1
        logger.debug('Will retry query status for %s after %s seconds. retries=%s' % (
            poller, countdown, retries))
        check_status_until_finished.subtask(
            args=(poller_name, result_handler_name, params),
            kwargs={'queue': queue},
            countdown=countdown,
            retries=retries,
            queue=queue,
        ).apply_async(headers={
            'queried_times': queried_times + 1,
            'ts_query_started': ts_query_started
        })
        return

    # 将查询结果转换为最终结果
    logger.info('Status query for %s finished, result=%s.' %
                (poller, poll_result))
    if result_handler_name is not None:
        result_handler_cls = ResultHandlerRegister.handler_map[result_handler_name]
        result_handler_cls(params).final_result_handler(poll_result)


class Healthz(BasePollerTaskStatus):
    max_retries = 1
    default_retry_delay_seconds = 1
    overall_timeout_seconds = 2

    def query_status(self):
        n = self.params.get("n", 0)
        return PollStatus(
            status=PollResultStatus.DONE.value, result=n + 1, is_exception=False)
