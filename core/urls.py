from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.contrib import admin

from core.test_views import auth
from treso import views as treso_views
from perm import views as perm_views
from core import views as core_views

from core.routers import router



urlpatterns = [

	path('admin/', admin.site.urls),

	# Authentication
	path('kraken/api/auth/login', core_views.login, name='auth.login'),
	path('kraken/api/auth/login_callback', core_views.login_callback, name='auth.login_callback'),
	path('kraken/api/auth/badge', core_views.login_badge, name="auth.badge"),
	path('kraken/api/auth/me', core_views.me, name='auth.me'),
	path('kraken/api/auth/logout', core_views.logout, name='auth.logout'),
	
	path('kraken/api/admin/settings', core_views.admin_settings),
	path('kraken/api/core/user', core_views.user_information),
	path('kraken/api/core/semester/state', core_views.semestre_state),
	path('kraken/api/core/semester/credit', core_views.semester_beginning_credit),
	path('kraken/api/current/semester', core_views.current_semester),

	# Include other application urls
	path('kraken/api/perms/', include('perm.urls')),
	path('kraken/api/treso/', include('treso.urls')),
	path('kraken/api/payutc/', include('payutc.urls')),

	# Include routers
	path('kraken/api/', include(router.urls)),
]
