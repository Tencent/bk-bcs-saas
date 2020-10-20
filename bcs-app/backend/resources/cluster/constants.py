# -*- coding: utf-8 -*-
from backend.utils.basic import ChoicesEnum


# COES: container orchestration engines
class ClusterCOES(ChoicesEnum):
    BCS_K8S = "k8s"
    MESOS = "mesos"

    _choices_labels = ((BCS_K8S, "k8s"), (MESOS, "mesos"))
