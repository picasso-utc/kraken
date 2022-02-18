from constance import config
from django.db.models import Q, Count
from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, permission_classes

from core import auth as auth_view
from core import models as core_models
from core import serializers as core_serializers
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, CanAccessMenuFunctionnalities
from core.services import ginger as g
from core.services.current_semester import get_current_semester, get_request_semester
from core.services.ginger import GingerClient
from core.settings import CONSTANCE_CONFIG


# Auth API View

@api_view(['POST'])
def login_badge(request, format=None):
    """Authentification avec le badge_uid et le PIN"""
    return auth_view.login_badge(request, format)


@api_view(['POST'])
def login_username(request, format=None):
    """Authentification avec le login et le PIN"""
    return auth_view.login_username(request, format)


@api_view(['GET'])
def login(request, format=None):
    """Redirection vers le CAS pour obtenir un ticket"""
    return auth_view.login(request, format)


@api_view(['GET'])
def login_callback(request, format=None):
    """
    Callback du CAS
    Connexion à l'API Weezevent avec le ticket du CAS
    Création d'une session
    """
    return auth_view.login_callback(request, format)


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser,))
def logout(request, format=None):
    """Déconnexion, destruction de la session"""
    return auth_view.logout(request, format)


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser,))
def me(request, format=None):
    """Information d'un utilisateur connecté"""
    return auth_view.me(request, format)


class PosteViewSet(viewsets.ModelViewSet):
    """ViewSet pour les postes disponibles au Pic (prez, treso, ...)"""
    serializer_class = core_serializers.PosteSerializer
    queryset = core_models.Poste.objects.all()
    permission_classes = (IsAdminUser,)


class MemberViewSet(viewsets.ModelViewSet):
    """
    Viewset pour les membres du Pic
    Membre : combinaison d'un semestre, d'un utilisateur et d'un poste
    """
    serializer_class = core_serializers.MemberSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        # Tri par semestre
        qs = core_models.Member.objects
        return get_request_semester(qs, self.request)


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def user_information(request, format=None):
    """
    Obtenir des informations via ginger à partir d'un login
    """
    login = request.GET.get('login', '')
    g = GingerClient()
    user = g.get_user_info(login)
    if user['status'] == 200:
        return JsonResponse(user['data'])
    return JsonResponse({'error': 'Une erreur s\'est produite'}, status=500)


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def semestre_state(request):
    """
    Renvoie la somme des factures payées du semestre (émises et reçues)
    """
    return JsonResponse(core_models.Semestre.objects.get(pk=config.SEMESTER).get_paid_bills())


@api_view(['GET', 'PUT'])
@permission_classes((IsAdminUser,))
def semester_beginning_credit(request):
    """
    Renvoie le solde au début du semestre actuel | Sauf si
    l'utilisateur spécifie un semester (avec le paramètre GET "semester")
    """
    semesterId = request.GET.get("semester", config.SEMESTER)
    semester = core_models.Semestre.objects.get(pk=semesterId)
    serializer = core_serializers.SemestreSerializer(semester)
    if request.method == 'PUT':
        semester.solde_debut = request.data['solde_debut']
        semester.save()
    return JsonResponse({'solde': int(semester.solde_debut)})


# ViewSets

class SemestreViewSet(viewsets.ModelViewSet):
    """Viewset pour gérer les semestres"""
    serializer_class = core_serializers.SemestreSerializer
    queryset = core_models.Semestre.objects.all()
    permission_classes = (IsMemberUser,)


class PeriodeTVAViewSet(viewsets.ModelViewSet):
    """
    PeriodeTVA ViewSet
    """
    permission_classes = (IsAdminUser,)
    queryset = core_models.PeriodeTVA.objects.all()
    serializer_class = core_serializers.PeriodeTVASerializer


class UserRightViewSet(viewsets.ModelViewSet):
    """
    UserRight Viewset
    """
    permission_classes = (IsAdminUser,)
    queryset = core_models.UserRight.objects.all()
    serializer_class = core_serializers.UserRightSerializer


def get_ginger_info(login, right, name, ginger=None):
    """Renvoie structure de données d'un utilisateur avec Ginger"""
    if not ginger:
        ginger = g.GingerClient()
    ginger_response = ginger.get_user_info(login)
    data = {'right': right, 'login': login, 'name': name}
    if ginger_response['status'] != 200:
        data['user'] = None
    else:
        data['user'] = ginger_response['data']
    if right == 'A':
        data['right_detail'] = 'Admin'
    elif right == 'M':
        data['right_detail'] = 'Membre'
    elif right == 'N':
        data['right_detail'] = 'Aucun droit'
    return data


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    """Classe pour gérer les utilisateurs depuis le site"""

    permission_classes = (IsAdminUser,)

    def list(self, request):
        # Récupération utilisateurs avec droit Admin et Membre
        queryset = core_models.UserRight.objects.filter(Q(right='A') | Q(right='M'))
        serializer = core_serializers.UserRightSerializer(queryset, many=True)
        # Récupération des informations des utilisateurs via Ginger
        # Ajout des droits correspondants
        ginger = g.GingerClient()
        users = []
        for i, user in enumerate(serializer.data):
            users.append(get_ginger_info(user['login'], user['right'], user['name'], ginger))
        return JsonResponse({'users': users})

    def create(self, request):
        # Création ou mise à jour d'un utilisateur
        serializer = core_serializers.UserRightSerializer(request.data)
        user = serializer.data
        new_user, created = core_models.UserRight.objects.update_or_create(
            login=user['login'],
            defaults={'right': user['right'], 'name': user['name']}
        )
        user = core_serializers.UserRightSerializer(new_user).data
        user = get_ginger_info(user['login'], user['right'], user['name'])
        return JsonResponse({'user': user})


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_team(request, format=None):
    """Renvoie les membres de l'équipe du semestre courant"""
    queryset = core_models.Member.objects.filter(semestre__id=get_current_semester())
    serializer = core_serializers.MemberAstreinteSerializer(queryset, many=True)
    team = serializer.data
    for member in team:
        # Nombre d'astreintes notées et totales ajoutées
        member["rated_astreintes"] = 0
        member["total_astreintes"] = len(member["astreinte_set"])
        for astreinte in member["astreinte_set"]:
            if astreinte["note_orga"] > 0:
                member["rated_astreintes"] += 1
        member.pop("astreinte_set")

    return JsonResponse({'team': serializer.data})


def get_constance_params():
    """Renvoi les attributs de config"""
    return {key: config.__getattr__(key) for key in CONSTANCE_CONFIG.keys()}


@api_view(['GET', 'POST'])
@permission_classes((IsAdminUser,))
def admin_settings(request, format=None):
    """
    Permet d'obtenir ou de mettre à jour tous les paramètres de configuration.
    """
    if request.method == 'GET':
        return JsonResponse({'settings': get_constance_params()})

    elif request.method == 'POST':
        if 'settings' in request.data:
            for key, value in request.data['settings'].items():
                config.__setattr__(key, value)
        return JsonResponse({'settings': get_constance_params()})


@api_view(['GET', 'POST'])
@permission_classes((IsMemberUser,))
def current_semester(request):
    """Obtenir ou mettre à jour le semestre courant"""
    if request.method == 'GET':
        semester = core_models.Semestre.objects.get(pk=config.SEMESTER)
        return JsonResponse(core_serializers.SemestreSerializer(semester).data)

    elif request.method == 'POST':
        if 'new_current_semester' in request.data:
            semester_id = request.data['new_current_semester']
            config.__setattr__('SEMESTER', semester_id)
            semester = core_models.Semestre.objects.get(pk=semester_id)
            return JsonResponse(core_serializers.SemestreSerializer(semester).data)


# @api_view(['GET'])
def badge_scan(request):
    login = None
    if request.method == 'GET':
        print(request.GET)
        badge_id = request.GET['badge_id']
        # Récupération depuis Ginger de badge_uid, name avec login
        try:
            ginger = g.GingerClient()
            ginger_response = ginger.get_badge_info(badge_id)
            first_name = ginger_response["data"]["prenom"]
            last_name = ginger_response["data"]["nom"]
            login = ginger_response["data"]["login"]
            new_user = core_models.PersonPerHour.objects.create(
                user_id=login,
                first_name=first_name,
                last_name=last_name,
            )
        except:
            return JsonResponse({"user": None})

    return JsonResponse({"user": login, "first_name": first_name, "last_name": last_name})


@api_view(['GET'])
def covid_stat(request):
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']
    answer = {}
    queryset = core_models.PersonPerHour.objects.all().filter(date_time__date__gte=start_date,
                                                              date_time__date__lte=end_date).values(
        'date_time__date').annotate(count=Count('user_id', distinct=True))
    for q in queryset:
        date = q['date_time__date'].strftime("%A %d %B %Y")
        answer[date] = q['count']
    # all_dates = core_models.PersonPerHour.objects.all().filter(date_time__date__gte=start_date, date_time__date__lte=end_date).distinct('date_time__date')
    # for date in all_dates:
    # count = core_models.PersonPerHour.objects.all().filter(date_time__date=date.date_time.date()).distinct('user_id').count()
    # answer[str(date.date_time.date())] = count
    return JsonResponse(answer)


class BlockedUserViewSet(viewsets.ViewSet):
    """ViewSet des utilisateurs bloqués"""

    def list(self, request):
        queryset = core_models.BlockedUser.objects.all()
        serializer = core_serializers.BlockedUserSerializer(queryset, many=True)
        return JsonResponse({'blocked_users': serializer.data})

    def create(self, request):
        login = request.data["login"]
        # Récupération depuis Ginger de badge_uid, name avec login
        ginger = g.GingerClient()
        ginger_response = ginger.get_user_info(login)
        justification = request.data["justification"]
        name = ginger_response["data"]["prenom"] + " " + ginger_response["data"]["nom"]
        badge_uid = ginger_response["data"]["badge_uid"]
        # Création utilisateur bloqué
        new_blocked_user = core_models.BlockedUser.objects.create(
            badge_uid=badge_uid,
            name=name,
            justification=justification,
        )
        queryset = core_models.BlockedUser.objects.get(pk=new_blocked_user.pk)
        serializer = core_serializers.BlockedUserSerializer(queryset)
        return JsonResponse({"user": serializer.data})

    @staticmethod
    def destroy(request, pk=None):
        if pk:
            core_models.BlockedUser.objects.filter(pk=pk).delete()
        return JsonResponse({})

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [CanAccessMenuFunctionnalities]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
