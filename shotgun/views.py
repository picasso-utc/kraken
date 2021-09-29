from django.utils import timezone

from rest_framework.response import Response
from rest_framework import viewsets

from core.models import UserRight
from core.permissions import FULL_CONNEXION
from core.services.payutc import PayutcClient
from shotgun import models as shotgun_models
from shotgun import serializers as shotgun_serializers


# Create your views here.

class CreneauViewSet(viewsets.ModelViewSet):
    queryset = shotgun_models.Creneau.objects.all()
    serializer_class = shotgun_serializers.CreneauSerializer

    def create(self, request, *args, **kwargs):
        right = request.session.get('right')
        login = request.session.get('login')
        has_full_connexion = request.session.get('connexion') == FULL_CONNEXION
        if (right == 'M' or right == 'A') and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response(status=403)


class UserInShotgunViewSet(viewsets.ModelViewSet):
    queryset = shotgun_models.UserInShotgun.objects.all()
    serializer_class = shotgun_serializers.UserInShotgunSerializer

    def create(self, request, *args, **kwargs):
        p = PayutcClient()
        p.login_admin()
        creneau = shotgun_models.Creneau.objects.filter(id=request.data['id_creneau']).values('actif', 'max_people','shotgunDate')
        if creneau[0]['actif'] and creneau[0]['shotgunDate'] < timezone.now():
            liste = p.auto_complete({'queryString': request.data['login']})
            if len(liste) == 1:
                data_temp = request.data.copy()
                data_temp['email'] = liste[0]['email']
                serializer = self.get_serializer(data=data_temp)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response({"Success": "shotgun réalisé"},status=200, headers=headers)
            else:
                return Response({"Fail": "votre login est invalide"},status=422)
        else:
            return Response({"Fail": "Le shotgun est terminé / n'a pas commencé"}, status=451)
