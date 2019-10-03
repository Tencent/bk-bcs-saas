# -*- coding: utf-8 -*-
import logging

from backend.components.bcs.mesos import MesosClient
from backend.utils.error_codes import error_codes
from backend.utils.errcodes import ErrorCode

logger = logging.getLogger(__name__)


class Namespace:

    @classmethod
    def delete(cls, access_token, project_id, cluster_id, ns_name):
        pass