from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from core import serializers as core_serializers
from core import models as core_models
from core import auth as auth_view
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser
from constance import config
from core.settings import CONSTANCE_CONFIG


# Auth API View

@api_view(['POST'])
def login_badge(request, format=None):
	"""Authenticate with badge_id"""
	return auth_view.login_badge(request, format)

@api_view(['GET'])
def login(request, format=None):
	"""Redirect to CAS with a callback pointing to login_callback"""
	return auth_view.login(request, format)

@api_view(['GET'])
def login_callback(request, format=None):
	"""Try login via PayUTC with CAS ticket"""
	return auth_view.login_callback(request, format)

@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def logout(request, format=None):
	return auth_view.logout(request, format)


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def me(request, format=None):
	return auth_view.me(request, format)


# ViewSets

class SemestreView(viewsets.ModelViewSet):
	serializer_class = core_serializers.SemestreSerializer
	queryset = core_models.Semestre.objects.all()
	permission_classes = (IsMemberUser,)


def get_constance_params():
	return [{'key': key, 'value': config.__getattr__(key)} for key in CONSTANCE_CONFIG.keys()]


['GET', 'POST']
@permission_classes((IsAdminUser, ))
def admin_settings(request, format=None):
	"""
	Endpoint qui permet d'obtenir tous les paramètres de configuration.
	"""
	if request.method == 'GET':
		return JsonResponse({'settings': get_constance_params()})

	elif request.method == 'POST':
		for param in request.data:
			config.__setattr__(param['key'], param['value'])
		return JsonResponse({'settings': get_constance_params()})


# @api_view(['POST'])
# @permission_classes((IsAdminUser, ))
# def admin_settings(request, format=None):
# 		for param in request.data:
# 			config.__setattr__(param['name'], param['val'])
# 		return JsonResponse({'settings': get_constance_params()})
