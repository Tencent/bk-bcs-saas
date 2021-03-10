# -*- coding: utf-8 -*-
"""聚合所有 components 系统"""
from backend.components.base import ComponentAuth
from backend.components.bcs_api import BcsApiClient

from .paas_cc import PaaSCCClient


class ComponentCollection:
    """可供使用的所有 Component 系统组合

    :param auth: 校验对象
    """

    def __init__(self, auth: ComponentAuth):
        self._auth = auth

    @property
    def paas_cc(self):
        return PaaSCCClient(auth=self._auth)

    @property
    def bcs_api(self):
        return BcsApiClient(auth=self._auth)
