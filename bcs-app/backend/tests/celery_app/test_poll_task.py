# -*- coding: utf-8 -*-
import time
from unittest import mock

import pytest

from backend.celery_app.poll_task import (
    CallbackHandler,
    CallbackStatus,
    NullResultHandler,
    PollingMetadata,
    PollingResult,
    PollTaskScheduler,
    TaskPoller,
    check_status_until_finished,
)


class FakeCheckTask:
    """A faked check task simulating celery Task object"""

    def __init__(self):
        self._subtask = mock.MagicMock()

    def __call__(self, *args, **kwargs):
        return check_status_until_finished(*args, **kwargs)

    def delay(self, *args, **kwargs):
        return check_status_until_finished(*args, **kwargs)

    def subtask(self, *args, **kwargs):
        return self._subtask


_fake_check_task = FakeCheckTask()


class BasePoller(TaskPoller):
    """Base poller using fake task"""

    def query(self) -> PollingResult:
        ...

    @classmethod
    def get_async_task(cls):
        return _fake_check_task


@pytest.fixture(autouse=True)
def reset_mocks():
    # Reset mocker
    BasePoller.get_async_task()._subtask = mock.MagicMock()


class TestPollTaskScheduler:
    def test_doing(self):
        class DoingPoller(BasePoller):
            def query(self) -> PollingResult:
                return PollingResult.doing(data={'foo': 'bar'})

        started_at = time.time()
        metadata = PollingMetadata(retries=0, query_started_at=started_at, queried_count=0)
        scheduler = PollTaskScheduler(DoingPoller({}, metadata), NullResultHandler)
        next_metadata = scheduler.run()
        assert next_metadata.retries == 0
        assert next_metadata.query_started_at == started_at
        assert next_metadata.queried_count == 1
        assert next_metadata.last_polling_data == {'foo': 'bar'}

    @pytest.mark.parametrize(
        'overall_timeout,result_status,result_data',
        [
            (-1, CallbackStatus.TIMEOUT, {}),
            (3600, CallbackStatus.NORMAL, {'foo': 'bar'}),
        ],
    )
    def test_timeout_and_normal(self, overall_timeout, result_status, result_data):
        class TimeoutedPoller(BasePoller):
            overall_timeout_seconds = overall_timeout

            def query(self) -> PollingResult:
                return PollingResult.done(data={'foo': 'bar'})

        class TimeoutedHandler(CallbackHandler):
            result = None
            poller = None

            def handle(self, result, poller):
                TimeoutedHandler.result = result
                TimeoutedHandler.poller = poller

        metadata = PollingMetadata(retries=0, query_started_at=time.time(), queried_count=0)
        scheduler = PollTaskScheduler(TimeoutedPoller({'param': 1}, metadata), TimeoutedHandler)
        next_metadata = scheduler.run()

        result = TimeoutedHandler.result
        assert next_metadata is None
        assert result.status == result_status
        assert result.data == result_data
        assert TimeoutedHandler.poller.params == {'param': 1}

    def test_exception(self):
        class ExceptionPoller(BasePoller):
            def query(self) -> PollingResult:  # type: ignore
                1 / 0

        class ExceptionHandler(CallbackHandler):
            result = None

            def handle(self, result, poller):
                ExceptionHandler.result = result

        started_at = time.time()
        metadata = PollingMetadata(
            retries=1, query_started_at=started_at, queried_count=1, last_polling_data={'foo': 'bar'}
        )
        scheduler = PollTaskScheduler(ExceptionPoller({}, metadata), ExceptionHandler)
        next_metadata = scheduler.run()
        assert next_metadata.retries == 2
        assert next_metadata.queried_count == 2
        assert next_metadata.last_polling_data == {'foo': 'bar'}
        assert ExceptionHandler.result is None

    def test_exception_no_continue(self):
        class ExceptionNoPoller(BasePoller):
            max_retries_on_error = 0

            def query(self) -> PollingResult:  # type: ignore
                1 / 0

        class ExceptionNoHandler(CallbackHandler):
            result = None

            def handle(self, result, poller):
                ExceptionNoHandler.result = result

        started_at = time.time()
        metadata = PollingMetadata(retries=0, query_started_at=started_at, queried_count=0)
        scheduler = PollTaskScheduler(ExceptionNoPoller({}, metadata), ExceptionNoHandler)
        next_metadata = scheduler.run()

        assert next_metadata is None
        result = ExceptionNoHandler.result
        assert result.status == CallbackStatus.EXCEPTION
        assert result.is_exception
        assert result.message == 'exception: division by zero'


class TestTaskPoller:
    def test_continue(self):
        class DoingPoller(BasePoller):
            def query(self) -> PollingResult:
                return PollingResult.doing()

        DoingPoller.start({}, NullResultHandler)
        assert DoingPoller.get_async_task().subtask().apply_async.called

    def test_no_continue(self):
        class DonePoller(BasePoller):
            def query(self) -> PollingResult:
                return PollingResult.done(data={'foo': 'bar'})

        DonePoller.start({}, NullResultHandler)
        assert not BasePoller.get_async_task().subtask().apply_async.called
