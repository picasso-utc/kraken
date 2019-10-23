from rest_framework import serializers
from . import models as survey_models


class SurveyItemVoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = survey_models.SurveyItemVote
        exclude = list()


class SurveyItemSerializer(serializers.ModelSerializer):
    surveyitem_set = SurveyItemVoteSerializer(many=True, read_only=True)

    class Meta:
        model = survey_models.SurveyItem
        exclude = list()


class SurveySerializer(serializers.ModelSerializer):

    surveyitem_set = SurveyItemSerializer(many = True, read_only = True)

    class Meta:
        model = survey_models.Survey
        exclude = list()

