# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(autouse=True)
def setup_comp_settings(settings):
    """Setup required settings for unittests"""
    settings.BCS_API_PRE_URL = 'https://bcs-api.example.com'
