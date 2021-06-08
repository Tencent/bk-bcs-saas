# -*- coding: utf-8 -*-
from rest_framework import serializers

from .featureflag import ClusterFeatureType


class ClusterFeatureTypeSLZ(serializers.Serializer):
    cluster_feature_type = serializers.ChoiceField(choices=ClusterFeatureType.get_choices())
