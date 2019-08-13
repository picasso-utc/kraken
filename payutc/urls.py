from django.urls import path, include
from rest_framework import routers

from payutc import views as payutc_views

urlpatterns = [

	path('user/autocomplete/<str:query>', payutc_views.user_autocomplete),

]
