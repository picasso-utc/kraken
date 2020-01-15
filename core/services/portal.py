import requests
from core.settings import PORTAL_URL


BASE_CONFIG = {
    'url': PORTAL_URL,
}


class PortalClient():
    """Ensemble de fonctions pour interagir avce l'API du portail des assos"""

    def __init__(self):
        self.config = BASE_CONFIG
        self.url = self.config['url']


    def get_assos(self):
        """Méthode pour récupérer les associations du Portail"""
        return self._apiCall(method="GET", path="assos")


    def _apiCall(self, method, path, data = None, parameters = None):
        """Fonction effecutant les appels API sur le Portail des assos"""

        uri = self.url + path
        response = requests.request(method=method, url=uri, data=data, params = parameters)
        return self._buildResponse(response)


    def _buildResponse(self, api_response):
        """Fonction pour construire une réponse à une requête API"""

        response = {
            'data' : api_response.json(),
            'status' : api_response.status_code
        }
        return response

    


