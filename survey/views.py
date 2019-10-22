from rest_framework import viewsets
from . import serializers as survey_serializers
from .import models as survey_models
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
