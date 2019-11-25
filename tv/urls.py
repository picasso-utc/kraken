from django.urls import path, include
from rest_framework import routers

from tv import views as tv_views

urlpatterns = [
	path('public/media', tv_views.get_public_media),
	path('orders', tv_views.get_next_order_lines_for_tv)
]
