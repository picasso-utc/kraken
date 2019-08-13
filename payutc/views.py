from rest_framework.decorators import api_view, permission_classes
from core.services.payutc import PayutcClient
from django.http import JsonResponse



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