from django.urls import path

from payutc import views as payutc_views

urlpatterns = [
	path('user/autocomplete/<str:query>', payutc_views.user_autocomplete),
	path('public/articles', payutc_views.get_sorted_articles),
	path('public/beers/sells', payutc_views.get_beers_sells),
	path('public/drinks/sells', payutc_views.get_sells),
]
