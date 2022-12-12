from django.utils import timezone

from rest_framework.response import Response
from rest_framework import viewsets

from core.models import UserRight
from core.permissions import FULL_CONNEXION
from core.services.ginger import GingerClient
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

    def make_shotgun(self, request, max):
        try:
            login = request.data['login']

            g = GingerClient()
            ginger_response = g.get_user_info(login)

            request.data['email'] = ginger_response['data']['mail']

            cur_nb = shotgun_models.Creneau.objects.select_related('user').filter(
                userinshotgun__id_creneau=request.data['id_creneau']
            ).count()

            if cur_nb < max:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response({"Success": "Shotgun réalisé"}, status=200, headers=headers)
            else:
                return Response({"Fail": "Maximum de personnes déjà atteint"}, status=429)
        except Exception:
            return Response({"Fail": "Votre login est invalide"}, status=422)

    def create(self, request, *args, **kwargs):
        id_creneau = request.data['id_creneau']

        try:
            creneau = shotgun_models.Creneau.objects.get(id=id_creneau)

            if hasRight(request):
                return self.make_shotgun(request, creneau.max_people)
            else:
                if creneau.actif and creneau.shotgunDate < timezone.now():
                    return self.make_shotgun(request, creneau.max_people)
                elif not creneau.actif:
                    return Response({"Fail": "Le shotgun est terminé"}, status=423)
                elif creneau.shotgunDate > timezone.now():
                    return Response({"Fail": "Le shotgun n'a pas commencé"}, status=425)
        except Exception:
            return Response({"Fail": "Ce shotgun n'existe pas"}, status=404)
