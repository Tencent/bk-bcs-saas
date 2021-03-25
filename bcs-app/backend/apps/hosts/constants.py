# -*- coding: utf-8 -*-
from backend.utils.basic import ChoicesEnum


class TaskStatus(ChoicesEnum):
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    REVOKED = "REVOKED"
    FINISHED = "FINISHED"

    _choices_labels = ((RUNNING, "RUNNING"), (FAILED, "FAILED"), (REVOKED, "REVOKED"), (FINISHED, "FINISHED"))


SCR_URL = ""


try:
    from .constants_ext import SCR_URL
except ImportError:
    pass
