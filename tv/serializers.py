from rest_framework import serializers
from tv import models as tv_models


class WebTVConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = tv_models.TVConfiguration
        exclude = list()


class WebTVSerializer(serializers.ModelSerializer):
    class Meta:
        model = tv_models.WebTV
        exclude = list()

class TVMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = tv_models.TVMedia
        exclude = list()