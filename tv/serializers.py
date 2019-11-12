from rest_framework import serializers
from tv import models as tv_models


class WebTVLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = tv_models.WebTVLink
        exclude = list()


class WebTVSerializer(serializers.ModelSerializer):
	link = WebTVLinkSerializer(read_only=True) 
	link_id = serializers.PrimaryKeyRelatedField(queryset=tv_models.WebTVLink.objects.all())
	class Meta:
		model = tv_models.WebTV
		exclude = list()


class WebTVMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = tv_models.WebTVMedia
        exclude = list()