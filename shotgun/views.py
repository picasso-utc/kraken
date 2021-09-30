from django.utils import timezone

from rest_framework.response import Response
from rest_framework import viewsets

from core.models import UserRight
from core.permissions import FULL_CONNEXION
from core.services.payutc import PayutcClient
from shotgun import models as shotgun_models
from shotgun import serializers as shotgun_serializers


# Create your views here.

def hasRight(request):
    right = request.session.get('right')
    login = request.session.get('login')
    has_full_connexion = request.session.get('connexion') == FULL_CONNEXION
    if (right == 'M' or right == 'A') and (
            UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion:
        return True
    else:
        return False


class CreneauViewSet(viewsets.ModelViewSet):
    queryset = shotgun_models.Creneau.objects.all()
    serializer_class = shotgun_serializers.CreneauSerializer

    def create(self, request, *args, **kwargs):
        if hasRight(request):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response(status=403)

    def list(self, request, pk=None):
        if hasRight(request):
            queryset = shotgun_models.Creneau.objects.all()
            serializer = shotgun_serializers.CreneauSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response(status=403)


class UserInShotgunViewSet(viewsets.ModelViewSet):
    queryset = shotgun_models.UserInShotgun.objects.all()
    serializer_class = shotgun_serializers.UserInShotgunSerializer

    def list(self, request, pk=None):
        if hasRight(request):
            queryset = shotgun_models.UserInShotgun.objects.all()
            serializer = shotgun_serializers.UserInShotgunSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response(status=403)

    def make_shotgun(self, request,max):
        p = PayutcClient()
        p.login_admin()
        data_temp = request.data.copy()
        liste = p.auto_complete({'queryString': request.data['login']})
        if len(liste) == 1:
            data_temp['email'] = liste[0]['email']
            nbListe = shotgun_models.Creneau.objects.select_related('user').filter(userinshotgun__id_creneau=request.data['id_creneau']).count()
            if nbListe < max:
                serializer = self.get_serializer(data=data_temp)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response({"Success": "shotgun réalisé"}, status=200, headers=headers)
            else:
                return Response({"Fail": "maximim de personnes déjà atteint"}, status=429)
        else:
            return Response({"Fail": "votre login est invalide"}, status=422)

    def create(self, request, *args, **kwargs):
        if hasRight(request):
            creneau = shotgun_models.Creneau.objects.filter(id=request.data['id_creneau']).values('max_people')
            return self.make_shotgun(request,creneau[0]['max_people'])
        else:
            creneau = shotgun_models.Creneau.objects.filter(id=request.data['id_creneau']).values('actif', 'max_people',
                                                                        'shotgunDate')
            if creneau[0]['actif'] and creneau[0]['shotgunDate'] < timezone.now():
                return self.make_shotgun(request,creneau[0]['max_people'])
            else:
                return Response({"Fail": "Le shotgun est terminé / n'a pas commencé"}, status=451)
