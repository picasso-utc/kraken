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
	path('api/auth/login', core_views.login, name='auth.login'),
	path('api/auth/login_callback', core_views.login_callback, name='auth.login_callback'),
	path('api/auth/badge', core_views.login_badge, name="auth.badge"),
	path('api/auth/me', core_views.me, name='auth.me'),
	path('api/auth/logout', core_views.logout, name='auth.logout'),
	
	path('api/admin/settings', core_views.admin_settings),
	path('api/core/user', core_views.user_information),
	path('api/current/semester', core_views.current_semester),

	# Include other application urls
	path('api/perms/', include('perm.urls')),
	path('api/treso/', include('treso.urls')),
	path('api/payutc/', include('payutc.urls')),

	# Include routers
	path('api/', include(router.urls)),
]
