from core.services.payutc import PayutcClient, PayutcException
from core.services.ginger import GingerClient
from core import models as core_models
from core import serializers as core_serializers
from core.settings import LOGIN_REDIRECT_URL

from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from core.services.current_semester import get_current_semester
import requests

# from rest_framework.authentication import BaseAuthentication
# from django.contrib.auth.backends import ModelBackend



def _set_session_information(request, username, sessionid, connexion="full"):
    """Set username, sessionid, rights and user information into the session"""
    request.session['login'] = username
    request.session['payutc_session'] = sessionid
    request.session['connexion'] = connexion

    # Check for user rights into the database
    try:
        user_right_queryset = core_models.UserRight.objects.get(login = username)
        user_right = core_serializers.UserRightSerializer(user_right_queryset)
    except core_models.UserRight.DoesNotExist:
        user_right = None
        request.session['right'] = None

    if user_right is not None and user_right.data and user_right.data['right'] != 'N':
        request.session['right'] = user_right.data['right'] 
        
        try:
            member_queryset = core_models.Member.objects.filter(userright_id= user_right.data['id'], semester_id=get_current_semester()).get()
            member = core_serializers.MemberSerializer(member_queryset)
        except core_models.Member.DoesNotExist:
            member = None
            request.session['member_id'] = None

        if member is not None and member.data and 'id' in member.data:
            request.session['member_id'] = member.data['id']

    # Get detailed user information with Ginger
    ginger = GingerClient()
    ginger_response = ginger.get_user_info(username)

    request.session['user'] = ginger_response['data']
    # 2h de session
    request.session.set_expiry(2*3600) 
    return request

def _get_params(request, format=None):
    """Get ticket, service and redirection params from the request"""
    ticket = request.GET.get('ticket')
    redirection = request.GET.get('redirect', '/api')
    # service = request.build_absolute_uri(reverse('auth.login_callback'))
    service = LOGIN_REDIRECT_URL
    service += '?redirect=' + redirection
    return ticket, service, redirection

def login_badge(request, format=None):
    """Authenticate with badge_id"""

    body_content = request.data
    badge_id = body_content["badge_id"]
    pin = body_content["pin"]
    p = PayutcClient()
    resp = p.process_request("login", "badge", params = {"badge_id": badge_id, "pin": pin})
    _set_session_information(request, resp['username'], resp['sessionid'])
    request.session.set_expiry(2*3600) 

    return JsonResponse(resp, status=200)


def login_username(request, format=None):
    """Authenticate with username and pin"""

    body_content = request.data
    username = body_content["username"]
    pin = body_content["pin"]
    ginger = GingerClient()
    ginger_response = ginger.get_user_info(username)
    badge_id = ginger_response['data']['badge_uid']
    p = PayutcClient()
    resp = p.process_request("login", "badge", params = {"badge_id": badge_id, "pin": pin})
    _set_session_information(request, resp['username'], resp['sessionid'], 'menu')
    request.session.set_expiry(2*3600) 

    return JsonResponse(resp, status=200)


def login(request, format=None):
    """Redirect to CAS with a callback pointing to login_callback"""
    ticket, service, redirection = _get_params(request)
    url = f"https://cas.utc.fr/cas/login?service={service}"
    return redirect(url)


def login_callback(request, format=None):
    """Try login via PayUTC with CAS ticket"""
    ticket, service, redirection = _get_params(request)
    payutc = PayutcClient()

    # If login successfully, add info to session, redirect to the front
    try:
        resp = payutc.login_cas(ticket, service)
        _set_session_information(request, resp['username'], resp['sessionid'])
        return redirect(redirection)

    # Else return error
    except PayutcException as error:
        return JsonResponse(error.response.json().get('error', {}),
                                                status_code=status.HTTP_400_BAD_REQUEST)


def me(request, format=None):
    """Retrieve session information"""
    login = request.session.get('login')
    right = request.session.get('right')
    user = request.session.get('user')
    connexion = request.session.get('connexion')
    return JsonResponse({
        'authenticated': login is not None,
        'login': login,
        'right': right,
        'user': user,
        'connexion': connexion
    })


def logout(request, format=None):
    """Delete session and redirect to CAS logout"""
    request.session.flush()
    requests.request(method='GET', url="https://cas.utc.fr/cas/logout")
    return JsonResponse({})

def login_user_from_session(request):
	login = request.session.get('login')
	if login:
		# TODO Create user ?
		request.user = UserModel(login=login, is_admin=is_authorized_login(login))
		return request.user
	return None



# class APIAuthentication(BaseAuthentication):
# 	"""
# 	Authenticate User frow request, used in the API
# 	"""

# 	def authenticate(self, request):
# 		"""
# 		Return the user from the JWT sent in the request
# 		"""
# 		# TODO Merge with AdminSiteBackend ??
# 		user = login_user_from_session(request)
# 		return (user, None) if user else None



# class AdminSiteBackend(ModelBackend):
# 	"""
# 	Authenticate User from email - password, used in the admin site
# 	"""

# 	def authenticate(self, request, username=None, password=None):
# 		# Try to fetch user from session
# 		user = login_user_from_session(request)

# 		# Try to fetch user with credentials
# 		if not user:
# 			try:
# 				user = UserModel.objects.get(**{UserModel.USERNAME_FIELD: username})
# 				if not user.check_password(password):
# 					return None
# 			except UserModel.DoesNotExist:
# 				return None

# 		# Check if admin
# 		if not user.is_admin:
# 			raise ValidationError(
# 				_("This account is not allowed."),
# 				code='not_allowed',
# 			)
# 		return user

# 	def get_user(self, login):
# 		if login:
# 			return UserModel(login=login, is_admin=is_authorized_login(login))
# 		else:
# 			return None
