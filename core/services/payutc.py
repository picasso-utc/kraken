from datetime import datetime
from math import ceil
from core.settings import PAYUTC_APP_KEY, PAYUTC_APP_URL, PAYUTC_SYSTEM_ID, PAYUTC_FUN_ID
import requests
from rest_framework.exceptions import APIException, NotFound



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
	'badge_id': 		None,
	'badge_pin': 		None,
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
	# 			POINT D'ENTREE
	# ============================================================

	

	

	# ============================================================
	# 			LOGIN
	# ============================================================

	def cas(self, params):
		# fun_id = self.get_config('fun_id')
		# app_key = self.get_config('app_key')
		data = {
			"service" : params["service"],
			"ticket" : params["ticket"]
			# 'fun_id' : fun_id['fun_id']
		}
		# data['fun_id'] = str(data['fun_id'])
		print(data)
		return self.request('post', 'GESARTICLE/loginCas2', data, api='services')

	def badge(self, params):
		fun_id = self.get_config('fun_id')
		return self.request('post', 'POSS3/loginBadge2', 
							data={"badge_id": params["badge_id"], "pin": params["pin"]},
							api='services')
	dispatch = {
    	'login': {
			'badge' : badge,
			'cas' : cas,
		},
	}

	def process_request(self, service, method, params):
		return self.dispatch[service][method](self, params)


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
		# if data.get('fun_id') == 'from_config':
		# data['fun_id'] = self.config['fun_id']
		if method == 'get':
			request_config['params'].update(data)
		else:
			request_config['json'] = data
		if 'request_config' in kwargs:
			request_config.update(kwargs['request_config'])

		# Make the request
		print(request_config)
		
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
			# raise NotFound("blbla")
			# raise APIException()
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

		raise AttributeError(f"'{name}' is not a valid request")	

	def list_routes(self, **kwargs):
		"""List all available routes"""
		url = kwargs.get('base_url', self.config['base_url']+'/resources')
		params = kwargs.get('params', { 'system_id': self.config['system_id'] })
		headers = kwargs.get('headers', {
			'Content-Type': 'application/json',
			'nemopay-version': self.config['nemopay_version'],
		})
		print(url)
		print(params)
		response = requests.get(url, params=params, headers=headers)
		if is_success(response.status_code):
			return response.json()
		raise PayutcException('Cannot list routes', response)


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

	def __login(self, response):
		if type(response) is not dict or not response.get('sessionid'):
			raise PayutcException('Login failed', response)
		self.config['session_id'] = response.get('sessionid')
		return response

	def login(self, method: str, **kwargs):
		method = self.__get_and_set_config('method', method)
		login_function = get_attr(self, f"login_{method}", None)
		if login_function and callable(login_function):
			return login_function(**kwargs)
		else:
			raise NotImplementedError(f"Login method '{method}' is not implemented")

	def is_loggued(self):
		return bool(self.config.get('session_id'))

	def get_user_details(self):
		return self.request('post', 'MYACCOUNT/getUserDetails', api='services')

	def login_cas(self, ticket: str=None, service: str=None):
		ticket = self.__get_and_set_config('cas_ticket', ticket)
		service = self.__get_and_set_config('cas_service', service)
		response = self.request('post', 'SELFPOS/loginCas2', { 'ticket': ticket, 'service': service }, api='services')
		return self.__login(response)

	def login_app(self, app_key: str=None):
		app_key = self.__get_and_set_config('app_key', app_key)
		response = self.request('post', 'POSS3/loginApp', { 'key': app_key }, api='services')
		return self.__login(response)

	def login_user(self, login: str=None, password: str=None):
		login = self.__get_and_set_config('mail', login)
		password = self.__get_and_set_config('password', password)
		response = self.request('post', 'SELFPOS/login2', { 'login': login, 'password': password }, api='services')
		return self.__login(response)

	def login_badge(self, pin: int=None, badge_id: str=None):
		badge_id = self.__get_and_set_config('badge_id', badge_id)
		pin = self.__get_and_set_config('badge_pin', pin)
		response = self.request('post', 'POSS3/loginBadge2', { 'badge_id': badge_id, 'pin': pin }, api='services')
		return self.__login(response)


	# ============================================================
	# 			SALES
	# ============================================================	

	def get_sales(self, **kwargs):
		keys = ('fun_id', 'start', 'end', 'offset', 'row_count', 'order_desc',
						'product_id__in', 'buyer_id__in', 'category_id__in')
		data = self.get_values_or_config(kwargs, *keys)
		data['start'] = self.format_datetime(data['start'])
		data['end'] = self.format_datetime(data['end'])
		return self.request('post', 'GESSALES/getSales', data, **kwargs, api='services')

	def get_sales_by_chunk(self, **kwargs):
		options = kwargs.copy()
		options['row_count'] = kwargs.get('chunk_size', DEFAULT_CHUNK_SIZE)
		first = self.get_sales(**options)
		yield first

		# Iterate over the remaining calls
		nb_call = ceil(first['count'] / options['row_count'])
		for i in range(1, nb_call):
			options['offset'] = options['row_count'] * i
			yield self.get_sales(**options)

	def get_nb_sell(self, **kwargs):
		data = self.get_values_or_config(kwargs, 'obj_id', 'fun_id', 'start', 'end')
		if 'start' in data:
			data['start'] = self.format_datetime(data['start'])
		if 'end' in data:
			data['end'] = self.format_datetime(data['end'])
		return self.request('post', 'STATS/getNbSell', data, api='services')
		

	# ============================================================
	# 			WEB TRANSACTIONS
	# ============================================================	

	def create_transaction(self, **kwargs):
		keys = ('items', 'mail', 'return_url', 'fun_id', 'callback_url')
		data = self.get_values_or_config(kwargs, *keys)
		data['fun_id'] = str(data['fun_id'])
		return self.request('post', 'WEBSALE/createTransaction', data, **kwargs, api='services')

	def get_transaction(self, **kwargs):
		data = self.get_values_or_config(kwargs, 'tra_id', 'fun_id')
		return self.request('post', 'WEBSALE/getTransactionInfo', data, **kwargs, api='services')



	# ============================================================
	# 			USERRIGHT
	# ============================================================

	def auto_complete(self, data):
		data = {'queryString': data['queryString']}
		return self.request('post', 'USERRIGHT/userAutocomplete', data, api='services')


	def get_sales(self, data):
		fun_id = self.get_config('fun_id')
		data = {'start': data['start'], 'end': data['end'], 'row_count': data['row_count'], 'fun_id': self.config['fun_id']}
		return self.request('post', 'GESSALES/getSales', data, api='services')


	# ============================================================
	# 			ARTICLES
	# ============================================================	

	def get_articles(self):
		fun_id = self.get_config('fun_id')
		return self.request('post', 'SELFPOS/getArticles', fun_id, api='services')

	def set_product(self, data = {}):
		data['fun_id'] = BASE_CONFIG['fun_id']
		return self.request('post', 'GESARTICLE/setProduct', data, api='services')


	def get_export(self, **kwargs):
		data = self.get_values_or_config(kwargs, 'fun_id', 'start', 'end', 'event_id')
		if 'start' in data:
			data['start'] = self.format_datetime(data['start'])
		if 'end' in data:
			data['end'] = self.format_datetime(data['end'])
		return self.request('post', 'TRESO/getExport', data, api='services')


