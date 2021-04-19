# -*- coding: utf-8 -*-
import pytest

from backend.utils.error_codes import CallableAPIError


class TestCallableAPIError:
    @pytest.mark.parametrize(
        'message,args,kwargs,expected',
        [
            ('new', [], {}, 'new'),
            ('new %s', ['foo'], {}, 'new foo'),
            ('new %(name)s', [], {'name': 'foo'}, 'new foo'),
        ],
    )
    def test_callable(self, message, args, kwargs, expected):
        err = CallableAPIError('foo_code', 'foo_message')
        assert err(message, *args, **kwargs).message == expected
