from django.urls import path

from treso2 import views as treso2_views

urlpatterns = [
    path('tvainfo/<int:id>', treso2_views.tva_info),
    path('factureRecue/<int:idsemestre>/<int:idcategorie>', treso2_views.facture_by_filter),
    path('stats', treso2_views.categorie_stats),
    path('excelFacture/<int:idsemestre>/<int:idcategorie>', treso2_views.excel_facture_generation),
    path('excelCheque', treso2_views.excel_cheque_generation)
]