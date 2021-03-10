from backend.components.base import ComponentAuth

from . import bcs_api, paas_cc


class StubComponentCollection:
    """使用 Stub 对象所有 Component 系统"""

    def __init__(self, auth: ComponentAuth):
        self._auth = auth

    @property
    def paas_cc(self):
        return paas_cc.StubPaaSCCClient(auth=self._auth)

    @property
    def bcs_api(self):
        return bcs_api.StubBcsApiClient(auth=self._auth)
