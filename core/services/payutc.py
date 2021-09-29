from datetime import datetime
import json
from django.core.cache import cache
from math import ceil
from core.settings import PAYUTC_APP_KEY, PAYUTC_APP_URL, PAYUTC_SYSTEM_ID, PAYUTC_FUN_ID
import requests
from rest_framework.exceptions import APIException, NotFound
from constance import config as live_config


DEFAULT_CHUNK_SIZE = 5000
ALLOWED_ACTIONS_MAP = {
	'get': 		'get',
	'find':		'get',
	'create': 	'post',
	'update': 	'put',
	'delete': 	'delete',
}
BASE_CONFIG = {
	'debug': 			False,
	'base_url': 		PAYUTC_APP_URL,
	'nemopay_version': 	'2018-07-03',
	'system_id': 		PAYUTC_SYSTEM_ID,
	'fun_id': 			PAYUTC_FUN_ID,
	# Login credentials
	'sessionid': 		None,
	'login_method': 	None,
	'badge_id': 		live_config.PAYUTC_CONNECTION_UID,
	'pin': 				live_config.PAYUTC_CONNECTION_PIN,
	'app_key':			PAYUTC_APP_KEY,
	'mail': 			None,
	'password': 		None,
	'cas_ticket':		None,
	'cas_service':		None,
}

def process_network_command(command, arg):
    send(dispatch[command](arg))

def is_success(status_code: int):
	return 200 <= status_code and status_code < 300

    
class PayutcException(Exception):

	def __init__(self, message, response=None, request=None):
		super().__init__(message)
		self.message = message
		self.response = response
		self.request = request

	def __str__(self):
		if self.response:
			detail = self.response.json().get('error', {}).get('message')
			if detail:
				return self.message + f" ({detail})"
		return self.message


class PayutcClient:
	"""
	The Payutc Client for Weezevent
	"""

	def __init__(self, sessionid=None, config: dict={}):
		self.config = { **BASE_CONFIG, **config }
		self.config['sessionid'] = sessionid



	# ============================================================
	# 			REQUETE MAKER
	# ============================================================
	

	def request(self, method: str, uri: str, data: dict={}, **kwargs):
		# Get all request configuration
		api = kwargs.get('api', 'resources')
		url = f"{self.config['base_url']}/{api}/{uri}"
		request_config = {
			'headers': {
				'Content-Type': 'application/json',
				'nemopay-version': self.config['nemopay_version'],
			}, 
			'params': self.get_config('app_key', 'system_id'),
			'cookies': { 'sessionid': self.config.get('sessionid') },
		}
		for kw in ('headers', 'params', 'cookies'):
			if kw in kwargs:
				request_config[kw].update(kwargs[kw])

		if data.get('fundation') == 'from_config':
			data['fundation'] = self.config['fun_id']

		if method == 'get':
			request_config['params'].update(data)
		else:
			request_config['json'] = data
		if 'request_config' in kwargs:
			request_config.update(kwargs['request_config'])

		# Make the request
		request = getattr(requests, method)
		response = request(url, **request_config)
		# Keep details if needed
		request_config['url'] = url
		request_config['data'] = data
		if self.config.get('debug'):
			self.last = {
				'response': response,
				'request': request_config,
			}
		# Return the response data
		if is_success(response.status_code) and not kwargs.get('return_response', False):
			return response.json()
		# Or raise an error
		if not is_success(response.status_code) and kwargs.get('raise_on_error', True):
			message = f"Error {response.status_code} on {method.upper()} {uri}"
			raise PayutcException(message, response, request_config)
		# Or simply return the response	
		return response	


	def pre_built_request(self, *pre_args, **pre_kwargs):
		def pre_built(*args, **kwargs):
			return self.request(*pre_args, *args, **pre_kwargs, **kwargs)
		return pre_built


	def __getattr__(self, name):
		if name in ALLOWED_ACTIONS_MAP:
			return self.pre_built_request(name)

		split = name.split('_')
		if len(split) == 2:
			action, resource = split
			if action in ALLOWED_ACTIONS_MAP:
				http_method = ALLOWED_ACTIONS_MAP[action]
				return self.pre_built_request(http_method, resource)
	

	# ============================================================
	# 			CONFIGURATION
	# ============================================================

	def get_values_or_config(self, kwargs, *keys) -> dict:
		return { key: kwargs.get(key, self.config.get(key))
						 for key in keys if key in kwargs or key in self.config }

	def get_config(self, *keys, all=False) -> dict:
		return self.config if all else { key: self.config.get(key) for key in keys }

	def set_config(self, key: str, value):
		self.config[key] = value
		return self

	def __get_and_set_config(self, key: str, value: None):
		if value is not None:
			self.config[key] = value
		return self.config[key]

	def format_datetime(self, dt: datetime) -> str:
			return dt.isoformat(timespec='seconds') if type(dt) is datetime else dt


	# ============================================================
	# 			LOGIN
	# ============================================================


	def cas(self, params):
		data = {
			"service" : params["service"],
			"ticket" : params["ticket"]
		}
		return self.request('post', 'GESARTICLE/loginCas2', data, api='services')

	def badge(self, params):
		fun_id = self.get_config('fun_id')
		return self.request('post', 'POSS3/loginBadge2', 
			data={"badge_id": params["badge_id"], "pin": params["pin"]},
			api='services')



	

	# ============================================================
	# 			LOGIN, AUTHENTICATION, AUTHORIZATION & ACCOUNT
	# ============================================================

	def __login(self, response):
		if type(response) is not dict or not response.get('sessionid'):
			raise PayutcException('Login failed', response)
		self.config['session_id'] = response.get('sessionid')
		return response

	def get_user_details(self):
		return self.request('post', 'MYACCOUNT/getUserDetails', api='services')

	def login_cas(self, ticket: str=None, service: str=None):
		ticket = self.__get_and_set_config('cas_ticket', ticket)
		service = self.__get_and_set_config('cas_service', service)
		response = self.request('post', 'SELFPOS/loginCas2', { 'ticket': ticket, 'service': service }, api='services')
		return self.__login(response)

	def login_badge(self, pin: int=None, badge_id: str=None, **kwargs):
		data = {"badge_id": badge_id, "pin": pin}
		response = self.request('post', 'POSS3/loginBadge2', data, api='services')
		return self.__login(response)

	def login_admin(self):
		sessionid = cache.get('sessionid')
		if not sessionid:
			badge_id = self.get_config('badge_id')["badge_id"]
			pin = str(self.get_config('pin')["pin"])
			sessionid = self.login_badge(pin=pin, badge_id=badge_id)['sessionid']
			cache.set('sessionid', sessionid, 30*60)
		self.config['sessionid'] = sessionid


	# ============================================================
	# 			SALES
	# ============================================================	

	def get_sales(self, **kwargs):
		"""
		Récupère les ventes avec possibilité de mettre pas mal de paramètres
		Date de début et date de fin
		Choisir des ids de produit ("product_id__in")
		Choisir dans une catégorie en particulier ("category_id__in")
		Choisir un acheteur en particulier ("buyer_id__in")
		Ordre des items
		L'API renvoie pas toutes les ventes, système de pagination pouant être
		géré ave offset et row_count. 
		Exemple: tu as 40 000 ventes que tu veux pas récupérer d'un coup pour pas faire
		crasher ton app mais par paquet de 10 000 ventes
		Tu vas mettre dans toutes tes requetes row_count=10000, et successivement
		mettre offset = 0, offset = 10000, offset= 20000 et offset=30000
		En fait offset c'est l'index du premier élément que tu veux récupérer et
		row_count la quantité à partir de cet index que tu veux récupérer.
		En général tu auras pas le nombre total de ventes donc tu itères jusqu'à
		que ce que tu récupères soit inférieur à row_count. C'est à dire que
		là avec row_count=10000 et offset=30000 tu auras 10000 élément mais si tu 
		continues avec offset=40000 tu auras 0 élément car le 40 000ème élément
		n'existe pas.
		"""
		keys = ('fun_id', 'start', 'end', 'offset', 'row_count', 'order_desc',
						'product_id__in', 'buyer_id__in', 'category_id__in')
		data = self.get_values_or_config(kwargs, *keys)
		if 'start' in data:
			data['start'] = self.format_datetime(data['start'])
		if 'end' in data:
			data['end'] = self.format_datetime(data['end'])
		return self.request('post', 'GESSALES/getSales', data, **kwargs, api='services')

	def get_nb_sell(self, **kwargs):
		"""Obtiens le nombre de ventes d'un article entre deux dates"""
		data = self.get_values_or_config(kwargs, 'obj_id', 'fun_id', 'start', 'end')
		if 'start' in data:
			data['start'] = self.format_datetime(data['start'])
		if 'end' in data:
			data['end'] = self.format_datetime(data['end'])
		return self.request('post', 'STATS/getNbSell', data, api='services')


	# ============================================================
	# 			USERRIGHT
	# ============================================================

	def auto_complete(self, data):
		"""A partir d'un string récupère les utilisateur spouvant y correspondre"""
		data = {'queryString': data['queryString']}
		print('AUTOCOMPLETE')
		return self.request('post', 'USERRIGHT/userAutocomplete', data, api='services')


	# ============================================================
	# 			ARTICLES
	# ============================================================	

	def get_articles(self):
		"""Récupère tous les articles sur Weez"""
		fun_id = self.get_config('fun_id')
		return self.request('post', 'SELFPOS/getArticles', fun_id, api='services')

	def set_product(self, data = {}):
		"""Crée un nouvel article sur Weez"""
		data['fun_id'] = BASE_CONFIG['fun_id']
		return self.request('post', 'GESARTICLE/setProduct', data, api='services')

	def get_export(self, **kwargs):
		"""Pour la tréso, obtiens un export entre deux dates"""
		data = self.get_values_or_config(kwargs, 'fun_id', 'start', 'end', 'event_id')
		if 'start' in data:
			data['start'] = self.format_datetime(data['start'])
		if 'end' in data:
			data['end'] = self.format_datetime(data['end'])
		return self.request('post', 'TRESO/getExport', data, api='services')


	# ============================================================
	# 			PATCH
	# ============================================================	

	def patch_api_rest(self, service, method, id, sessionid=None, params=None, **data):
		"""
		Méthode générique pour faire des PATCH sur Weez
		Qu'est ce qu'un PATCH ? Quand on veut mettre à jour un objet
		(avec la méthode PUT des services HTTP)
		on est obligé d'ajouter toutes les valeurs qui le composent.
		Si par exemple un article a un nom et qu'on envoie pas de nom
		au moment de l'update, Weez va considérer que le nom de l'article
		doit maintenant être null. C'est des fois chiant de tout renvoyer
		pour une mise à jour et en fait la méthode PATCH des services HTTP
		y remédient. 
		Si tu as un article avec un prix et un nom et qu'en utilisant PATCH tu
		renvoies que le nom, seul le nom sera mis à jour
		Ici la méthode est générique tu peux envoyer n'importe quel servide, méthode,
		paramètre.
		Elle est notamment utilisée dans Perm/ Models.py pour les articles
		Jete un coup d'oeil si ça te paraît utile pour faire une mise à jour pour
		autre chose
		"""
		if params is None:
			params = {'system_id': PAYUTC_SYSTEM_ID, 'sessionid': self.config['sessionid']}
		headers = {'nemopay-version': '2018-07-03', 'Content-Type': 'application/json'}
		url = "https://api.nemopay.net/" + service + "/" + method + "/" + str(id)
		r = requests.patch(url, json=data, params=params, headers=headers)
		if r.status_code != 200:
			raise NemopayClientException(r.text)
		return json.loads(r.text)