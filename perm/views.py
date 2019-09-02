from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from rest_framework import viewsets
from . import serializers as perm_serializers
from .import models as perm_models
from django.shortcuts import render
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, IsMemberUserOrReadOnly
import datetime

class PermViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.PermSerializer
    queryset = perm_models.Perm.objects.all()
    permission_classes = (IsMemberUserOrReadOnly,)


class CreneauViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.CreneauSerializer
    queryset = perm_models.Creneau.objects.all()
    permission_classes = (IsMemberUserOrReadOnly,)


@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def get_creneau_sales(request, id):
    c = perm_models.Creneau.objects.get(pk=id)
    return JsonResponse(c.get_justificatif_information())


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.ArticleSerializer
    queryset = perm_models.Article.objects.all()
    permission_classes = (IsAdminUser,)

class SignatureViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.SignatureSerializer
    queryset = perm_models.Signature.objects.all()
    permission_classes = (IsAdminUser,)


@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def create_payutc_article(request, id):
    # Endpoint qui permet d'obtenir, pour un article de pk {id}, d'enregistrer l'article dans PayUTC.
    article = perm_models.Article.objects.get(pk=id)
    sessionid = request.session['payutc_session']
    article.create_payutc_article(sessionid)
    # TVConfiguration.objects.create(tv_id=1, url="http://beethoven.picasso-utc.fr/NextMenus", enable_messages=False)
    # TVConfiguration.objects.create(tv_id=2, url="http://beethoven.picasso-utc.fr/NextMenus", enable_messages=False)
    return JsonResponse({})


@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def get_article_sales(request, id):
    # Endpoint qui permet d'obtenir, pour un article de pk {id}, le nombre de ventes.
    article = perm_models.Article.objects.get(pk=id)
    sessionid = request.session['payutc_session']
    sales = article.update_sales(sessionid)
    return JsonResponse({'sales': sales})


@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def get_current_creneau(request):
    date = datetime.datetime.now()

    # On déterminer si la perm en cours est celle du matin, du midi ou du soir
    hour = date.time().hour
    creneau = 'M'
    if hour >= 16 :
        creneau = 'S'
    elif hour >= 11:
        creneau = 'D'
    
    queryset = perm_models.Creneau.objects.filter(creneau=creneau, date=date)
    serializer = perm_serializers.CreneauSerializer(queryset, many=True)
    current_creneau = dict()
    if serializer.data:
        current_creneau = serializer.data[0]
    return JsonResponse(current_creneau)




