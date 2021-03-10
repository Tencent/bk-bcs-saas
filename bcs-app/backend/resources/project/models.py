# -*- coding: utf-8 -*-
"""用于在系统内部使用的 Project 对象"""
from ..models import BaseContextedModel


class CtxProject(BaseContextedModel):
    """项目对象

    :param id: 项目 ID
    """

    def __init__(self, id: str):
        self.id = id

    def __str__(self):
        return f'<Project: {self.id}>'
