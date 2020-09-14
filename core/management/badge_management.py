from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from django.http import JsonResponse
from core import serializers as core_serializers
from core import models as core_models
from core import auth as auth_view
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, CanAccessMenuFunctionnalities
from constance import config
from core.settings import CONSTANCE_CONFIG
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from core.services.ginger import GingerClient
from core.services.current_semester import get_current_semester, get_request_semester
from core.services import ginger as g



class PersonPerHourViewSet(viewsets.ViewSet):
	"""ViewSet des utilisateurs bloqués"""
	def list(self, request):
		queryset = core_models.PersonPerHour.objects.all()
		serializer = core_serializers.PersonPerHourSerializer(queryset, many=True)
		return JsonResponse({'person_per_hour': serializer.data})

	def create(self, request):
		badge_id = request.data["badge_id"]
		# Récupération depuis Ginger de badge_uid, name avec login
		ginger = g.GingerClient()
		ginger_response = ginger.get_badge_info(badge_id)
		first_name = ginger_response["data"]["prenom"]
        last_name = ginger_response["data"]["nom"]
        username = ginger_response["data"]["username"]

		# Création de la ligne dans la bdd
		new_user = core_models.PersonPerHour.objects.create(
		    user_id = badge_uid,
		    first_name = first_name,
		    last_name = last_name,
		)
		serializer = core_serializers.BlockedUserSerializer(queryset)
		return JsonResponse({"user": serializer.data})

	def destroy(self, request, pk=None):
		if pk:
			core_models.PersonPerHour.objects.filter(pk=pk).delete()
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