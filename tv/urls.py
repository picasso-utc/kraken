from django.urls import path, include
from rest_framework import routers

from tv import views as tv_views

urlpatterns = [
	path('public/media', tv_views.get_public_media),
]
