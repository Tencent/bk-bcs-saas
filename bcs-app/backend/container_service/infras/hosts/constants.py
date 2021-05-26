# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


# 默认使用的标准运维业务ID
SOPS_BIZ_ID = ""

# 申请主机流程模板ID
APPLY_HOST_TEMPLATE_ID = ""

try:
    from .constants_ext import *  # noqa
except ImportError as e:
    logger.debug("Load extension failed: %s", e)
