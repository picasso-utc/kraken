import requests
from core.settings import GINGER_URL, GINGER_KEY


BASE_CONFIG = {
    'url': GINGER_URL,
    'key': GINGER_KEY,
}


class GingerException(Exception):

    def __init__(self, code, message):
        self.message = message
        self.code = code

    def __str__(self):
        return 'Ginger Exception (' + self.code + ') : ' + self.message


class GingerClient():
    """Ensemble de fonctions pour interagir avce l'API Ginger, outil de gestion des cotisants"""

    def __init__(self):
        self.config = BASE_CONFIG
        self.url = self.config['url']
        self.key = self.config['key']


    def get_user_info(self, username):
        
        return self._apiCall(method="GET", path="/" + username)


    def _apiCall(self, method, path, data = None, parameters = None):
        """Fonction effecutant les appels API sur Ginger/v1"""

        uri = self.url + path
        key = self.key

        response = requests.request(method=method, url=uri + "?key=" + key, data=data, params = parameters)

        return self._buildResponse(response)


    def _buildResponse(self, api_response):
        """Fonction pour construire une réponse à une requête API"""

        if api_response.status_code != 200:
            raise GingerException(api_response.status_code, api_response.json())

        response = {
            'data' : api_response.json(),
            'status' : api_response.status_code
        }

        return response

    


