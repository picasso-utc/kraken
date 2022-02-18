from django.urls import path

from covid import views as covid_view

urlpatterns = [
    path('occupation', covid_view.get_occupation)
]
