from django.urls import path, include
from rest_framework import routers

from treso import views as treso_views

urlpatterns = [
	path('tvainfo/<int:id>', treso_views.tva_info)
]
