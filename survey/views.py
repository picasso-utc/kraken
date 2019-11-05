from rest_framework import viewsets
from . import serializers as survey_serializers
from .import models as survey_models
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, IsMemberUserOrReadOnly, CanAccessMenuFunctionnalities, HasApplicationRight

class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = survey_serializers.SurveySerializer
    queryset = survey_models.Survey.objects.all()
    permission_classes = (IsMemberUser,)


class SurveyItemViewSet(viewsets.ModelViewSet):
    serializer_class = survey_serializers.SurveyItemSerializer
    queryset = survey_models.SurveyItem.objects.all()
    permission_classes = (IsMemberUser,)


class SurveyItemVoteViewSet(viewsets.ModelViewSet):
    serializer_class = survey_serializers.SurveyItemVoteSerializer
    queryset = survey_models.SurveyItemVote.objects.all()
    permission_classes = (IsMemberUser,)


@api_view(['GET'])
def get_public_surveys(request):
    queryset = survey_models.Survey.objects.filter(visible=True)
    serializer = survey_serializers.SurveySerializer(queryset, many=True)
    surveys = serializer.data
    for survey in surveys:
        for item in survey['surveyitem_set']:
            del item["surveyitemvote_set"]
    return JsonResponse({'surveys' : surveys})