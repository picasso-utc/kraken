from rest_framework import serializers
from . import models as survey_models
from drf_extra_fields.fields import Base64ImageField



class SurveyItemVoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = survey_models.SurveyItemVote
        exclude = list()


class SurveyItemSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required = False, use_url=False)
    surveyitemvote_set = SurveyItemVoteSerializer(many=True, read_only=True)

    class Meta:
        model = survey_models.SurveyItem
        exclude = list()


class SurveySerializer(serializers.ModelSerializer):

    image = Base64ImageField(use_url=False)
    surveyitem_set = SurveyItemSerializer(many = True, read_only = True)

    class Meta:
        model = survey_models.Survey
        exclude = list()
