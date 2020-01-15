from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from django.http import JsonResponse
from core import serializers as core_serializers
from core import models as core_models
from core import auth as auth_view
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser
from constance import config
from core.settings import CONSTANCE_CONFIG
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from core.services.ginger import GingerClient
from core.services.current_semester import get_current_semester, get_request_semester


from core.services import ginger as g


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
@permission_classes((IsAuthenticatedUser, ))
def logout(request, format=None):
	"""Déconnexion, destruction de la session"""
	return auth_view.logout(request, format)


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
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
@permission_classes((IsMemberUser, ))
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
@permission_classes((IsAdminUser, ))
def semestre_state(request):
    """
    Renvoie la somme des factures payées du semestre (émises et reçues)
    """
    return JsonResponse(core_models.Semestre.objects.get(pk=config.SEMESTER).get_paid_bills())


@api_view(['GET', 'PUT'])
# TO REVIEW
@permission_classes((IsAdminUser, ))
def semester_beginning_credit(request):
    """
    Erenvoie le solde au début du semestre actuel | Sauf si 
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
	serializer_class = core_serializers.SemestreSerializer
	queryset = core_models.Semestre.objects.all()
	permission_classes = (IsMemberUser,)


class PeriodeTVAViewSet(viewsets.ModelViewSet):
    """
    PeriodeTVA endpoint
    """
    permission_classes = (IsAdminUser, )
    queryset = core_models.PeriodeTVA.objects.all()
    serializer_class = core_serializers.PeriodeTVASerializer



class UserRightViewSet(viewsets.ModelViewSet):
    """
    Userright endpoint
    """
    permission_classes = (IsAdminUser, )
    queryset = core_models.UserRight.objects.all()
    serializer_class = core_serializers.UserRightSerializer


class UserViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):

	permission_classes = (IsAdminUser,)

	def list(self, request):
		queryset = core_models.UserRight.objects.filter(Q(right='A') | Q(right='M'))
		serializer = core_serializers.UserRightSerializer(queryset, many=True)
		# Retrieve user from Ginger and add right details
		ginger = g.GingerClient()
		for i, user in enumerate(serializer.data):
			login = serializer.data[i]['login']
			ginger_response = ginger.get_user_info(login)

			if ginger_response['status'] != 200:
				serializer.data[i]['user'] = None
			else:
				serializer.data[i]['user'] = ginger_response['data']
			right = serializer.data[i]['right']
			if right == 'A':
				serializer.data[i]['right_detail'] = 'Admin'
			elif right == 'M':
				serializer.data[i]['right_detail'] = 'Membre'
		return JsonResponse({'users': serializer.data})


	def create(self, request):
		serializer = core_serializers.UserRightSerializer(request.data)
		user = serializer.data

		new_user, created = core_models.UserRight.objects.update_or_create(
			login=user['login'],
	        defaults={'right': user['right']}
	    )
		user = core_serializers.UserRightSerializer(new_user).data
		status = 200
		if created:
			status = 201
		ginger = g.GingerClient()
		ginger_response = ginger.get_user_info(user['login'])
		if ginger_response['status'] != 200:
			user['user'] = None
		else:
			user['user'] = ginger_response['data']
		if user['right'] == 'A':	
			user['right_detail'] = 'Admin'
		elif user['right'] == 'M':
			user['right_detail'] = 'Membre'
		elif user['right'] == 'N':
			user['right_detail'] = 'Aucun droit'

		return JsonResponse({'user': user})


@api_view(['GET'])
@permission_classes((IsAdminUser, ))
def get_team(request, format=None):

	queryset = core_models.Member.objects.filter(semestre__id=get_current_semester())
	serializer = core_serializers.MemberAstreinteSerializer(queryset, many=True)
	team = serializer.data
	for member in team : 
		member["rated_astreintes"] = 0
		member["total_astreintes"] = len(member["astreinte_set"])
		for astreinte in member["astreinte_set"]:
			if astreinte["note_orga"] > 0:
				member["rated_astreintes"] += 1
		member.pop("astreinte_set")

	return JsonResponse({'team': serializer.data})



def get_constance_params():
	return {key: config.__getattr__(key) for key in CONSTANCE_CONFIG.keys()}


@api_view(['GET', 'POST'])
@permission_classes((IsAdminUser, ))
def admin_settings(request, format=None):
	"""
	Endpoint qui permet d'obtenir tous les paramètres de configuration.
	"""
	if request.method == 'GET':
		return JsonResponse({'settings': get_constance_params()})

	elif request.method == 'POST':
		if 'settings' in request.data:
			for key, value in request.data['settings'].items():
				config.__setattr__(key, value)
		return JsonResponse({'settings': get_constance_params()})



@api_view(['GET', 'POST'])
@permission_classes((IsMemberUser, ))
def current_semester(request):

	if request.method == 'GET':
		semester = core_models.Semestre.objects.get(pk=config.SEMESTER)
		return JsonResponse(core_serializers.SemestreSerializer(semester).data)

	elif request.method == 'POST':
		if 'new_current_semester' in request.data:
			semester_id = request.data['new_current_semester']
			config.__setattr__('SEMESTER', semester_id)
			semester = core_models.Semestre.objects.get(pk=semester_id)
			return JsonResponse(core_serializers.SemestreSerializer(semester).data)


# Semester to check
class BlockedUserViewSet(viewsets.ViewSet):

	def list(self, request):
		queryset = core_models.BlockedUser.objects.all()
		serializer = core_serializers.BlockedUserSerializer(queryset, many=True)
		return JsonResponse({'blocked_users': serializer.data})

	def create(self, request):
		login = request.data["login"]
		# Retrieve information from Ginger (badge_uid, name)
		ginger = g.GingerClient()
		ginger_response = ginger.get_user_info(login)
		justification = request.data["justification"]
		name = ginger_response["data"]["prenom"] + " " + ginger_response["data"]["nom"]
		badge_uid = ginger_response["data"]["badge_uid"]
		new_blocked_user = core_models.BlockedUser.objects.create(
		    badge_uid = badge_uid,
		    name = name,
		    justification = justification,
		)
		queryset = core_models.BlockedUser.objects.get(pk=new_blocked_user.pk)
		serializer = core_serializers.BlockedUserSerializer(queryset)
		return JsonResponse({"user": serializer.data})


	def destroy(self, request, pk=None):
		
		if pk:
			core_models.BlockedUser.objects.filter(pk=pk).delete()
		return JsonResponse({})


	def get_permissions(self):
		"""
		Instantiates and returns the list of permissions that this view requires.
		"""
		if self.action == 'list':
			permission_classes = [IsMemberUser]
		else:
			permission_classes = [IsAdminUser]
		return [permission() for permission in permission_classes]
