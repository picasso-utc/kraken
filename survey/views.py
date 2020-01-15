from rest_framework import viewsets
from . import serializers as survey_serializers
from .import models as survey_models
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, IsMemberUserOrReadOnly, CanAccessMenuFunctionnalities, HasApplicationRight
import os

@permission_classes((IsMemberUser, ))
class SurveyViewSet(viewsets.ModelViewSet):
    """Survey ViewSet"""
    serializer_class = survey_serializers.SurveySerializer
    queryset = survey_models.Survey.objects.filter(completed=False)
    permission_classes = (IsMemberUser,)

@permission_classes((IsMemberUser, ))
class SurveyItemViewSet(viewsets.ModelViewSet):
    """SurveyItem ViewSet"""
    serializer_class = survey_serializers.SurveyItemSerializer
    queryset = survey_models.SurveyItem.objects.all()
    permission_classes = (IsMemberUser,)


@permission_classes((IsMemberUser, ))
class SurveyItemVoteViewSet(viewsets.ModelViewSet):
    """SurveyItemVote ViewSet"""
    serializer_class = survey_serializers.SurveyItemVoteSerializer
    queryset = survey_models.SurveyItemVote.objects.all()
    permission_classes = (IsMemberUser,)


@api_view(['GET'])
def get_public_surveys(request):
    """
    Renvoie les sondages publiquement
    Suppression des votes pour chaque item
    """
    queryset = survey_models.Survey.objects.filter(visible=True, completed=False)
    serializer = survey_serializers.SurveySerializer(queryset, many=True)
    surveys = serializer.data
    for survey in surveys:
        for item in survey['surveyitem_set']:
            del item["surveyitemvote_set"]
    return JsonResponse({'surveys' : surveys})


@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def get_history_surveys(request):
    """
    Renvoie les sondages archivées, c'est à dire
    dont l'attribut completed est  True
    """
    queryset = survey_models.Survey.objects.filter(completed=True)
    serializer = survey_serializers.SurveySerializer(queryset, many=True)
    surveys = serializer.data
    return JsonResponse({'surveys' : surveys})


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def get_public_survey(request, id=None):
    """
    Renvoie un sondage spécifique pour un utilisateur connecté
    Ajoute si l'utilisateur connecté a voté pour un item du sondage
    Suppression des votes pour chaque item 
    """
    login = request.session['login']
    queryset = survey_models.Survey.objects.filter(visible=True, completed=False, id=id)
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
@permission_classes((IsMemberUser, ))
def delete_survey(request, pk=None):
    """
        Supprime un sondage : 2 cas
        - Le sondage a déjà été archivée (attribut completed = True)
        Alors il est définitivement supprimé du système
        - Le sondage n'est pas archivée
        Dans ce cas on compte les résultats en % et le nombre de votants
        On ajoute ces infos sur Survey (nb de votes) et SurveyItem (% de votes)
        Puis on supprime tous les SurveyItemVote, on supprime donc les
        informations confidentiels que sont le vote d'une personne pour un item
        Suppression également des images liées au sondage et aux items
    """
    queryset = survey_models.Survey.objects.get(pk=pk)
    # Si déjà archivée
    if queryset.completed:
        queryset.delete()
        return JsonResponse({"response": "Le sondage a été supprimé de l'historique."})
    # Sinon
    serializer = survey_serializers.SurveySerializer(queryset)
    survey = serializer.data
    total_votes = 0
    # Pour tous les items dans le sondage
    for survey_item in survey["surveyitem_set"]:
        survey_item_id = survey_item["id"]
        # Incrémentation du nombre de votants pour un item
        survey_item_votes = len(survey_item["surveyitemvote_set"])
        total_votes += survey_item_votes
        # Mise à jour de l'item du sondage en mettant le nombre de votes
        surveyitem_request = survey_models.SurveyItem.objects.get(pk=survey_item_id)
        surveyitem_request.votes = survey_item_votes
        if surveyitem_request.image:
            if os.path.isfile(surveyitem_request.image.path):
                # Suppression de l'image du SurveyItem
                os.remove(surveyitem_request.image.path)
                surveyitem_request.image = None
        surveyitem_request.save()
        for survey_item_vote in survey_item["surveyitemvote_set"]:
            # Suppression des votants pour tous les items du sondage
            survey_models.SurveyItemVote.objects.filter(survey_item_id=survey_item_id).delete()
    # Suppression de l'image du sondage
    if queryset.image:
        if os.path.isfile(queryset.image.path):
            os.remove(queryset.image.path)
            queryset.image = None
    # Enregistrement dans le sondage du nombre total de votants
    queryset.total_votes = total_votes
    queryset.completed = True
    queryset.visible = False
    queryset.save()
    return JsonResponse({})


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def get_survey_results(request, id=None):
    """
    Renvoie les résultats d'un sondage en particulier en % pour un utilisateur connecté
    S'assure que l'utilisateur a bien voté et que le sondage est bien disponible
    """
    login = request.session['login']
    queryset = survey_models.Survey.objects.filter(visible=True, completed=False, id=id)
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
    """
    Vote pour un sondage pour utilisateur connecté
    S'assure que le sondage est disponible et que l'utilisateur n'a pas déjà voté
    Dans le cas d'un sondage multi choix on s'assure que l'utilisateur n'a pas
    déjà voté pour cet item
    """
    login = request.session['login']
    queryset = survey_models.Survey.objects.filter(visible=True, id=survey_id, completed=False)
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
    """
    Annulation d'un vote pour un sondage
    """
    login = request.session['login']
    survey_models.SurveyItemVote.objects.filter(survey_item_id=item_id, login=login).delete()

    return JsonResponse({})