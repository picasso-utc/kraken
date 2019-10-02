from rest_framework import serializers
from tv import models as tv_models


class WebTVConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = tv_models.TVConfiguration


class WebTVSerializer(serializers.ModelSerializer):
    class Meta:
        model = tv_models.WebTV