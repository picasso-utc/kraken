from django.urls import path

from tv import views as tv_views

urlpatterns = [
	path('public/media', tv_views.get_public_media),
	path('orders', tv_views.get_next_order_lines_for_tv),
	path('surveys', tv_views.get_tv_public_surveys),
	path('qrcode', tv_views.generate_qr_code)
]
