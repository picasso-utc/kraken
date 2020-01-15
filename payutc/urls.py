from django.urls import path, include
from rest_framework import routers

from payutc import views as payutc_views

urlpatterns = [
	path('user/autocomplete/<str:query>', payutc_views.user_autocomplete),
	path('public/articles', payutc_views.get_sorted_articles),
	path('public/beers/sells', payutc_views.get_beers_sells)
]
