from rest_framework import serializers
from tv import models as tv_models


class WebTVLinkSerializer(serializers.ModelSerializer):
	url = serializers.URLField()
	class Meta:
		model = tv_models.WebTVLink
		exclude = list()


class WebTVSerializer(serializers.ModelSerializer):
	link = WebTVLinkSerializer(read_only=True) 
	link_id = serializers.PrimaryKeyRelatedField(queryset=tv_models.WebTVLink.objects.all(), source="link")
	class Meta:
		model = tv_models.WebTV
		exclude = list()


class WebTVMediaSerializer(serializers.ModelSerializer):
	media = serializers.FileField(allow_empty_file=True, allow_null=True, use_url=False)
	class Meta:
		model = tv_models.WebTVMedia
		exclude = list()