from django.urls import path, include
from rest_framework import routers

from chopin import views as chopin_views

urlpatterns = [
    path('newsletter', chopin_views.get_newsletters),
    path('perms', chopin_views.get_calendar)
]
