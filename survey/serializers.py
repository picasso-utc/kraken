from rest_framework import serializers
from . import models as survey_models


class SurveyItemVoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = survey_models.SurveyItemVote
        fields = list()


class SurveyItemSerializer(serializers.ModelSerializer):
    vote = serializers.PrimaryKeyRelatedField(queryset = survey_models.SurveyItemVote.objects.all())

    class Meta:
        model = survey_models.SurveyItem
        fields = list()


class SurveySerializer(serializers.ModelSerializer):

    survey_item_set = SurveyItemSerializer(many = True, read_only = True)

    class Meta:
        model = survey_models.Survey
        exclude = list()

