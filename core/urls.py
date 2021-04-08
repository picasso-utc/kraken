from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.contrib import admin

from core.test_views import auth
from treso import views as treso_views
from perm import views as perm_views
from core import views as core_views

from core.routers import router
from django.conf.urls.static import static
from . import settings


urlpatterns = [

	# Authentication
	path('api/auth/login', core_views.login, name='auth.login'),
	path('api/auth/login_callback', core_views.login_callback, name='auth.login_callback'),
	path('api/auth/badge', core_views.login_badge, name="auth.badge"),
	path('api/auth/username', core_views.login_username, name="auth.username"),
	path('api/auth/me', core_views.me, name='auth.me'),
	path('api/auth/logout', core_views.logout, name='auth.logout'),
	
	# Application Core
	path('api/admin/settings', core_views.admin_settings),
	path('api/core/user', core_views.user_information),
	path('api/core/semester/state', core_views.semestre_state),
	path('api/core/semester/credit', core_views.semester_beginning_credit),
	path('api/current/semester', core_views.current_semester),
	path('api/core/team', core_views.get_team),
	path('api/core/badge_scan', core_views.badge_scan),
	path('api/core/covid_stat', core_views.covid_stat),

	# Inclusion URL application Perm
	path('api/perms/', include('perm.urls')),

	# Inclusion URL application Treso
	path('api/treso/', include('treso.urls')),

	# Inclusion URL application Payutc
	path('api/payutc/', include('payutc.urls')),

	# Inclusion URL application Survey
	path('api/surveys/', include('survey.urls')),

	# Inclusion URL application TV
	path('api/tv/', include('tv.urls')),

	# Inclusion fichier Router
	# Ce dernier contient les Viewset, 1 URL = 1 CRUD
	# CRUD = Create, Read, Update, Deete 
	path('api/', include(router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Route pour ajouter les médias