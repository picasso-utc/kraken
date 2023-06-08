from django.urls import path

from treso import views as treso_views

urlpatterns = [
    path('tvainfo/<int:id>', treso_views.tva_info),
    path('convention/<int:id>', treso_views.get_convention),
    path('conventions', treso_views.get_all_conventions),
    path('excel/factures', treso_views.excel_facture_generation),
    path('excel/cheques', treso_views.excel_cheque_generation),
    path('stats', treso_views.get_categories_stats),
    path('exonerations', treso_views.get_categories_exonerations)
]
