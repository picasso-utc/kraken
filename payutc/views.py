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
from datetime import datetime



class GoodiesWinnerViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
					mixins.DestroyModelMixin,
					mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
	"""
	ViewSet pour gérer les vainqueurs des goodies
	Création aléatoire à partir d'une date de début et de fin
	Récupération des vainqueurs
	Mise à jour du statut (Récupérer ou pas)
	Suppression
	"""

	permission_classes = (IsMemberUserOrReadOnly,)

	def list(self, request):
		queryset = payutc_models.GoodiesWinner.objects.all()
		serializer = payutc_serializers.GoodiesWinnerSerializer(queryset, many=True)
		return JsonResponse({'winners': serializer.data})


	def create(self, request):
		"""Méthode pour générer 20 vainqueurs des goodies parmis les non-membres du Pic"""

		# Récupération des ventes entre une date de début et une date de fin
		# START doit être au format "AAAA-MM-JJ"
		# END doit être au format "AAAA-MM-JJ"
		# ROW_COUNT représente le nombre maximum de ventes récupérées
		sessionid = request.session['payutc_session']
		p = PayutcClient()
		p.login_admin()
		start = request.data['start_date'] + "T00:00:01.000Z"
		end = request.data['end_date'] + "T23:00:00.000Z"
		ROW_COUNT = 20000
		sales = p.get_sales(start=start, end=end, row_count=ROW_COUNT)['transactions']

		# Recherche des membres dans le Pic actuel
		pic_members = []
		queryset = core_models.UserRight.objects.filter(Q(right='A') | Q(right='M'))
		serializer = core_serializers.UserRightSerializer(queryset, many=True)
		# Récupération des logins des membres du Pic pour les supprimer par la suite de la génération
		for i, user in enumerate(serializer.data):
			login = serializer.data[i]['login']
			pic_members.append(login)

		# Récupération aléatoire d'utilisateurs
		goodies_winners = []
		nb_sales = len(sales)
		while (len(goodies_winners) < 20):
			# Tant qqu'on a pas 20 vainqueurs on itère
			random_value = random.randint(1, nb_sales)
			user = sales[int(random_value) - 1]['rows'][0]['payments'][0]['buyer']
			user_description = user["first_name"] + " " + user["last_name"]
			# Si l'utilisateur n'est pas un membre du Pic ou un login déjà dans la liste des vainqueurs, ajout 
			if (user["username"] not in pic_members and user_description not in goodies_winners):
				goodies_winners.append(user_description)
				payutc_models.GoodiesWinner.objects.create(winner=user_description, picked_up=False)

		# Renvoi des données
		queryset = payutc_models.GoodiesWinner.objects.all()
		serializer = payutc_serializers.GoodiesWinnerSerializer(queryset, many=True)
		return JsonResponse({'winners': serializer.data})


	def update(self, request, pk=None):
		winner_instance = payutc_models.GoodiesWinner.objects.get(pk=pk)
		winner_instance.picked_up = not winner_instance.picked_up
		winner_instance.save()
		serializer = payutc_serializers.GoodiesWinnerSerializer(winner_instance)
		return JsonResponse(serializer.data)

	def delete(self, request):
		payutc_models.GoodiesWinner.objects.all().delete()
		return JsonResponse({'winners': []})


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser, ))
def user_autocomplete(request, query, format=None):
	"""
	Récupération à parti d'une query string des utilisateurs
	sur Payutc pouvant être susceptible de ressembler à la query
	"""

	data = {
		'queryString': query
	}
	sessionid = request.session['payutc_session']
	p = PayutcClient()
	p.login_admin()
	return JsonResponse({'users': p.auto_complete(data)})


@api_view(['GET'])
def get_sorted_articles(request, format=None):
	"""Obtention des articles du Pic en ventes et mise en forme"""
	p = PayutcClient()
	articles = p.get_articles()

	sorted_articles = {
		3: 	('softs', []),
		11: ('bieresPression', []),
		10: ('bieresBouteille', []),
		9: 	('snacksSucres', []),
		17: ('snacksSales', []),
		184:('glace', []),
		221:('petitDej', []),
		199:('pampryls', []),
	}

	for article in articles :

		# IDs des catégories
		# ==================
		# Softs : 3
		# Bières pression : 11
		# Bières bouteille : 10
		# Snacks sucrés : 9
		# Snacks salés : 17
		# Glacé : 184
		# Petit dej : 221
		# Pampryls : 199

		if (article["active"]) :
			bin = sorted_articles.get(article["categorie_id"])
			if bin is not None:
				bin[1].append({
					'name' : article["name"],
					'price' : article["price"]
				})

	return JsonResponse(dict(sorted_articles.values()), status=200)


@api_view(['POST'])
def get_beers_sells(request):
	"""
	Obtention des ventes dans la journée courante des ids mis en paramètres
	Méthode utilisée publique, utilisée pour le duel des brasseurs en A19 
	"""
	beers = request.data['beers']
	response = dict()

	current_date = (datetime.now()).strftime('%Y-%m-%d')
	start_date = current_date + "T00:00:01.000Z"
	end_date = current_date + "T23:59:59.000Z"

	p = PayutcClient()
	p.login_admin()

	duels = beers.keys()
	for duel in duels: 
		response[duel] = dict()
		duel_beers = beers[duel].keys()
		for beer in duel_beers:
			beer_id = beers[duel][beer]['id']
			nb_sells = p.get_nb_sell(obj_id=beer_id, start=start_date, end=end_date)
			response[duel][beer] = dict()
			response[duel][beer]['id'] = beers[duel][beer]['id']
			response[duel][beer]['quantity'] = nb_sells

	return JsonResponse({'beers': response}, status=200)
