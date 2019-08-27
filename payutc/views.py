from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, mixins
from core.services.payutc import PayutcClient
from django.http import JsonResponse
from django.db.models import Q
from payutc import models as payutc_models
from core import models as core_models
from core import serializers as core_serializers
from payutc import serializers as payutc_serializers
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, IsMemberUserOrReadOnly
import random



class GoodiesWinnerViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
					mixins.DestroyModelMixin,
					mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):

	permission_classes = (IsAdminUser,)

	def list(self, request):
		queryset = payutc_models.GoodiesWinner.objects.all()
		serializer = payutc_serializers.GoodiesWinnerSerializer(queryset, many=True)
		return JsonResponse({'winners': serializer.data})


	def create(self, request):
		"""Méthode pour générer 20 vainqueurs des goodies parmis les non membres du Pic"""

		# Récupération des ventes entre une date de début et une date de fin
		# START doit être au format "AAAA-MM-JJ"
		# END doit être au format "AAAA-MM-JJ"
		# ROW_COUNT représente le nombre maximum de ventes récupérées
		sessionid = request.session['payutc_session']
		p = PayutcClient(sessionid)
		start = request.data['start_date'] + "T00:00:01.000Z"
		end = request.data['end_date'] + "T23:00:00.000Z"
		# START =	"2019-06-10T00:00:01.000Z"
		# END = "2019-06-15T23:00:00.000Z"
		ROW_COUNT = 20000
		sales = p.get_sales({'start': start, 'end': end, 'row_count': ROW_COUNT})['transactions']

		# Recherche des membres dans le Pic actuel
		pic_members = []
		queryset = core_models.UserRight.objects.filter(Q(right='A') | Q(right='M'))
		serializer = core_serializers.UserRightSerializer(queryset, many=True)
		for i, user in enumerate(serializer.data):
			login = serializer.data[i]['login']
			pic_members.append(login)

		# Récupération aléatoire d'utilisateurs
		goodies_winners = []
		nb_sales = len(sales)
		while (len(goodies_winners) < 20):
			random_value = random.randint(1, nb_sales)
			user = sales[int(random_value) - 1]['rows'][0]['payments'][0]['buyer']
			user_description = user["first_name"] + " " + user["last_name"]

			if (user["username"] not in pic_members and user_description not in goodies_winners):
				goodies_winners.append(user_description)
				payutc_models.GoodiesWinner.objects.create(winner=user_description, picked_up=False)

		# Renvoi des données
		queryset = payutc_models.GoodiesWinner.objects.all()
		serializer = payutc_serializers.GoodiesWinnerSerializer(queryset, many=True)
		return JsonResponse({'winners': serializer.data})


	def update(self, request, pk=None):
		print(pk)
		winner_instance = payutc_models.GoodiesWinner.objects.get(pk=pk)
		winner_instance.picked_up = not winner_instance.picked_up
		winner_instance.save()
		serializer = payutc_serializers.GoodiesWinnerSerializer(winner_instance)
		return JsonResponse(serializer.data)

	def delete(self, request):
		payutc_models.GoodiesWinner.objects.all().delete()
		return JsonResponse({'winners': []})


@api_view(['GET'])
def user_autocomplete(request, query, format=None):
	"""Authenticate with badge_id"""

	data = {
		'queryString': query
	}
	sessionid = request.session['payutc_session']
	p = PayutcClient(sessionid)
	return JsonResponse({'users': p.auto_complete(data)})

	# return auth_view.login_badge(request, format)