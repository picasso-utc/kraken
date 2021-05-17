from django.urls import path, include
from rest_framework import routers

from covid import views as covid_view

urlpatterns = [
	path('occupation', covid_view.get_occupation)
]
