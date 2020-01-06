from django.urls import path, include
from rest_framework import routers

from survey import views as survey_views

urlpatterns = [
	path('public', survey_views.get_public_surveys),
	path('public/<int:id>', survey_views.get_public_survey),
	path('public/results/<int:id>', survey_views.get_survey_results),
	path('public/vote/<int:survey_id>/<int:item_id>', survey_views.vote_survey),
	path('public/vote/cancel/<int:item_id>', survey_views.cancel_vote),
	path('history', survey_views.get_history_surveys),
	path('delete/<int:pk>', survey_views.delete_survey)
]
