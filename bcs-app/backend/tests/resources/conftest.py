# -*- coding: utf-8 -*-
import os
import uuid

from kubernetes import client

from backend.tests.conftest import TESTING_API_SERVER_URL


class FakeBcsKubeConfigurationService:
    """Fake configuration service which return local apiserver as config"""

    def __init__(self, *args, **kwargs):
        pass

    def make_configuration(self):
        configuration = client.Configuration()
        configuration.api_key = {"authorization": f'Bearer {os.environ.get("TESTING_SERVER_API_KEY")}'}
        configuration.verify_ssl = False
        configuration.host = TESTING_API_SERVER_URL
        return configuration
