from rest_framework.decorators import api_view
from core.services.payutc import PayutcClient
from rest_framework.response import Response
from django.shortcuts import redirect
import json


@api_view(['GET'])
def login_cas(request, format=None):
    """
        Authentification CAS avec gestion du callback
        Récupération username et sessionid sur Weez
        Crée une session dans l'API
    """

    service = "http://localhost:8000" + request.path
    ticket = request.GET.get('ticket')

    if ticket is None:
        url = f"https://cas.utc.fr/cas/login?service={service}"
        return redirect(url)

    payutc = PayutcClient()
    response = payutc.cas({"ticket": ticket, "service": service})
    request.session["username"] = response['username']
    request.session["sessionid"] = response['sessionid']

    return Response({"authentication": "successfull"})


@api_view(['POST'])
def login_badge(request, format=None):
    """
        Authentification avec badge et pin via Weez
        Récupération username et sessionid
        Crée une session dans l'API
    """
    body_content = json.loads(request.body)

    payutc = PayutcClient()
    response = payutc.badge({"badge_id": body_content["badge_id"], "pin": body_content["pin"]})

    request.session["username"] = response['username']
    request.session["sessionid"] = response['sessionid']
    request.session["permission"] = "admin"

    return Response({"authentication": "successfull"})


@api_view(['GET'])
def is_login(request, format=None):
    """Vérifie que l'utilisateur est bien connecté en regardant la session"""

    if request.session.get("username") and request.session.get("sessionid") and request.session.get("permission"):
        return Response({"login": True})
    return Response({"login": False})


@api_view(['GET'])
def get_user_permissions(request, format=None):
    """Récupère le rôle de l'utilisateur et le renvoie"""
    permission = request.session.get("permission")
    return Response({"permission": permission})


@api_view(['GET'])
def get_user_details(request, format=None):
    """Récupère les informations d'un utilisateur"""
    payutc = PayutcClient()
    routes = payutc.list_routes()
    # print(routes)
    # details = payutc.get_user_details

    # print(details.json())
    # print("ok")
    return Response(routes)
    # return Response(details)


@api_view(['GET'])
def logout(request, format=None):
    """Supprime la sessionde l'utilisateur"""
    session_keys = list(request.session.keys())
    for key in session_keys:
        del request.session[key]
    return Response({})
