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


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def get_public_survey(request, id=None):
    login = request.session['login']
    queryset = survey_models.Survey.objects.filter(visible=True, id=id)
    serializer = survey_serializers.SurveySerializer(queryset, many=True)
    surveys = serializer.data
    if len(surveys) > 0:
        survey = surveys[0]
        for item in survey['surveyitem_set']:
            vote = [v for v in item['surveyitemvote_set'] if v['login'] == login]
            if len(vote) > 0:
                item["voted"] = True
            else : 
                item["voted"] = False
            del item['surveyitemvote_set']

    return JsonResponse({'survey' : survey})


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def get_survey_results(request, id=None):
    login = request.session['login']
    queryset = survey_models.Survey.objects.filter(visible=True, id=id)
    serializer = survey_serializers.SurveySerializer(queryset, many=True)
    surveys = serializer.data
    if len(surveys) > 0:
        survey = surveys[0]
        votes = 0
        results = []
        found = False
        for item in survey['surveyitem_set']:
            votes += len(item['surveyitemvote_set'])
            item["votes"] = len(item['surveyitemvote_set'])
            vote_login = [v for v in item['surveyitemvote_set'] if v['login'] == login]
            if len(vote_login) > 0:
                found = True
                item["voted"] = True
            else :
                item["voted"] = False
            del item['surveyitemvote_set']

        for item in survey['surveyitem_set']:
            if votes > 0:
                result = {'id': item["id"], "votes": round((item["votes"]/votes) * 100,2)}
                results.append(result)

    if found:
        return JsonResponse({'results' : results})
    else :
        return JsonResponse({'error': 'Vous n\'avez pas participé à ce sondage'}, status = 409)


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def vote_survey(request, survey_id=None, item_id=None):

    login = request.session['login']
    queryset = survey_models.Survey.objects.filter(visible=True, id=survey_id)
    serializer = survey_serializers.SurveySerializer(queryset, many=True)
    surveys = serializer.data
    if len(surveys) > 0:
        survey = surveys[0]
        # Si multi choix non autorisé, on vérifie que l'utilisateur est pas déjà rentré
        if not survey["multi_choice"]:
            found = False
            for item in survey['surveyitem_set']:
                vote = [v for v in item['surveyitemvote_set'] if v['login'] == login]
                if len(vote) > 0:
                    found = True

            if found :
                return JsonResponse({'error': 'Vous avez déjà voté pour ce sondage.'}, status = 409)

            # Si pas trouvé on ajoute le vote
            survey_item_vote = survey_models.SurveyItemVote.objects.create(
                login=login,
                survey_item_id=item_id
            )
            return JsonResponse({})

        # Si multi choix autorisé on vérfiie simplement que l'utilisateur n'a pas déjà voté pour cet item
        queryset = survey_models.SurveyItem.objects.filter(id=item_id)
        serializer = survey_serializers.SurveyItemSerializer(queryset, many=True)
        survey_items = serializer.data
        print(survey_items)
        if len(survey_items) > 0:
            survey_item = survey_items[0]
            vote = [v for v in survey_item['surveyitemvote_set'] if v['login'] == login]
            if len(vote) > 0:
                return JsonResponse({'error': 'Vous avez déjà voté pour cet item.'}, status = 409)

            survey_item_vote = survey_models.SurveyItemVote.objects.create(
                login=login,
                survey_item_id=item_id
            )
            return JsonResponse({})

    return JsonResponse({'error': 'Une erreur est survenue'}, status = 500)


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def cancel_vote(request, item_id=None):

    login = request.session['login']
    survey_models.SurveyItemVote.objects.filter(survey_item_id=item_id, login=login).delete()

    return JsonResponse({})