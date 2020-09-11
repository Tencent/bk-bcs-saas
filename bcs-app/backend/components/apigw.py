# -*- coding: utf-8 -*-
import logging

from django.conf import settings

from backend.utils import requests

logger = logging.getLogger(__name__)


def get_api_public_key(api_name, app_code=None, app_secret=None):
    try:
        url = f"{settings.APIGW_HOST}/apigw/managementapi/get_api_public_key/"
        headers = {"BK-APP-CODE": app_code or settings.APP_ID, "BK-APP-SECRET": app_secret or settings.APP_TOKEN}
        params = {"api_name": api_name}
        data = requests.bk_get(url, params=params, headers=headers)
        return data.get("public_key")
    except Exception as e:
        logger.exception("get api public key failed: %s", e)
        return None
