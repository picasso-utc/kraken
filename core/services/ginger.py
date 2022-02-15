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


class GingerClient:
    """Ensemble de fonctions pour interagir avec l'API Ginger, outil de gestion des cotisants"""

    def __init__(self):
        self.config = BASE_CONFIG
        self.url = self.config['url']
        self.key = self.config['key']

    def get_user_info(self, username):
        """Méthode pour obtenir des informations à partir d'un login"""
        return self._apiCall(method="GET", path="/" + username)

    def get_badge_info(self, badge_id):
        """Méthode pour obtenir des informations à partir d'un badge"""
        return self._apiCall(method="GET", path="/badge/" + badge_id)

    def _apiCall(self, method, path, data=None, parameters=None):
        """Fonction effectuant les appels API sur Ginger/v1"""

        uri = self.url + path
        key = self.key

        response = requests.request(method=method, url=uri + "?key=" + key, data=data, params=parameters)

        return self._buildResponse(response)

    @staticmethod
    def _buildResponse(api_response):
        """Fonction pour construire une réponse à une requête API"""

        response = {
            'data': api_response.json(),
            'status': api_response.status_code
        }

        return response
