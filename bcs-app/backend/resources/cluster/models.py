# -*- coding: utf-8 -*-
"""用于在系统内部使用的 Cluster 集群建模"""
from ..models import BaseContextedModel


class CtxCluster(BaseContextedModel):
    """集群对象

    :param id: 集群 ID
    :param project_id: 集群所属项目 ID
    """

    def __init__(self, id: str, project_id: str):
        self.id = id
        self.project_id = project_id

    def __str__(self):
        return f'<Cluster: {self.project_id}-{self.id}>'
