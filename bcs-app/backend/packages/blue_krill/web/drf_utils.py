# -*- coding: utf-8 -*-
"""Utilities for DRF framework"""
import copy
from typing import List, Any

from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList


def stringify_validation_error(error: ValidationError) -> List[str]:
    """Transform DRF's ValidationError into a list of error strings

    >>> stringify_validation_error(ValidationError({'foo': ErrorDetail('err')}))
    ['foo: err']
    """
    results: List[str] = []

    def traverse(err_detail: Any, keys: List[str]):
        """Traverse error data to collect all error messages"""

        # Dig deeper when structure is list or dict
        if isinstance(err_detail, (ReturnList, list, tuple)):
            for err in err_detail:
                traverse(err, keys)
        elif isinstance(err_detail, (ReturnDict, dict)):
            for key, err in err_detail.items():
                # Make a copy of keys so the inner loop won't affect outer scope
                _keys = copy.copy(keys)
                if key != api_settings.NON_FIELD_ERRORS_KEY:
                    _keys.append(str(key))
                traverse(err, _keys)
        else:
            if not keys:
                results.append(str(err_detail))
            else:
                results.append('{}: {}'.format('.'.join(keys), str(err_detail)))

    traverse(error.detail, [])
    return sorted(results)
