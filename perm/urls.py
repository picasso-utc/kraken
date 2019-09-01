from django.urls import path, include
from rest_framework import routers

from perm import views as perm_views

urlpatterns = [
	path('payutc/article/<int:id>', perm_views.create_payutc_article),
	path('sales/article/<int:id>', perm_views.get_article_sales),
	path('sales/<int:id>', perm_views.get_creneau_sales)
]
