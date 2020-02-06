#  # -*- coding: utf-8 -*-

# # from sets import Set

from django.shortcuts import render
from rest_framework import viewsets
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from django.template.loader import render_to_string
from xlwt import Workbook
from PyPDF2 import PdfFileMerger, PdfFileReader
from core.services.payutc import PayutcClient
import os
from core.services.current_semester import get_current_semester
from core import models as core_models
from core import viewsets as core_viewsets
from perm import models as perm_models
from perm import serializers as perm_serializers
from treso import models as treso_models
from treso import serializers as treso_serializers
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser
from core.settings import APP_URL
from core.services.current_semester import get_request_semester
from core.services import excel_generation
import pdfkit


class CategorieFactureRecueViewSet(viewsets.ModelViewSet):
    """ViewSet des catégories de facture"""
    serializer_class = treso_serializers.CategorieFactureRecueSerializer
    queryset = treso_models.CategorieFactureRecue.objects.all()
    permission_classes = (IsAdminUser,)

class FactureRecueViewSet(viewsets.ModelViewSet):
    """ViewSet des factures reçues"""
    serializer_class = treso_serializers.FactureRecueSerializer
    permission_classes = (IsAdminUser,)
    def get_queryset(self):
        qs = treso_models.FactureRecue.objects
        return get_request_semester(qs, self.request)


class ChequeViewSet(viewsets.ModelViewSet):
    """ViewSet des chèques"""
    serializer_class = treso_serializers.ChequeSerializer
    queryset = treso_models.Cheque.objects.all()
    permission_classes = (IsAdminUser,)


class FactureEmiseViewSet(core_viewsets.RetrieveSingleInstanceModelViewSet):
    """ViewSet des factures émises"""
    single_serializer_class = treso_serializers.FactureEmiseWithRowsSerializer
    serializer_class = treso_serializers.FactureEmiseSerializer
    permission_classes = (IsAdminUser,)
    def get_queryset(self):
        qs = treso_models.FactureEmise.objects
        return get_request_semester(qs, self.request)


class FactureEmiseRowViewSet(viewsets.ModelViewSet):
    """ViewSet des lignes d'une facture émise"""
    serializer_class = treso_serializers.FactureEmiseRowSerializer
    queryset = treso_models.FactureEmiseRow.objects.all()
    permission_classes = (IsAdminUser,)


class ReversementEffectueViewSet(viewsets.ModelViewSet):
    """ViewSet des reversements"""
    serializer_class = treso_serializers.ReversementEffectueSerializer
    queryset = treso_models.ReversementEffectue.objects.all()
    permission_classes = (IsAdminUser,)


@api_view(['GET'])
@permission_classes((IsAdminUser, ))
def tva_info(request, id):
    """Obtention des informations de la tva"""
    periode = core_models.PeriodeTVA.objects.get(pk=id)

    # Pour la TVA déductible : on veut juste obtenir le montant total de TVA
    tva_deductible = sum([facture.get_total_taxes() for facture
        in treso_models.FactureRecue.objects.filter(date__gte=periode.debut, date__lte=periode.fin)])

    # Pour la TVA à déclarer :
    #   * On récupère toute la TVA sur PayUTC pendant cette période.
    #   * On récupère toute la TVA sur les factures émises pendant cette période.
    # Event_id hardcoded to 1
    sessionid = request.session['payutc_session']
    p = PayutcClient(sessionid)
    sales = p.get_export(start=periode.debut.isoformat(), end=periode.fin.isoformat(), event_id=1)
    payutc_tva_types = set(sale['pur_tva'] for sale in sales)

    factures_emises = treso_models.FactureEmiseRow.objects.prefetch_related('facture').filter(facture__date_creation__gte=periode.debut, facture__date_creation__lte=periode.fin)
    tva_types = payutc_tva_types.union(set(facture.tva for facture in factures_emises))

    tva_a_declarer = list()
    for tva_type in tva_types:
        tva_a_declarer.append({'pourcentage': tva_type,
                               'montant': sum([(1 - (100 / (100 + sale['pur_tva'])))*sale['total']*0.01 for sale in sales if sale['pur_tva'] == tva_type])
                               + sum(facture.get_total_taxes() * facture.qty for facture in factures_emises if facture.tva == tva_type)})

    return JsonResponse({'tva_deductible': tva_deductible,
                     'tva_a_declarer': tva_a_declarer,
                     'tva_a_declarer_total': sum(tva['montant'] for tva in tva_a_declarer)})


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_convention(request, id):
    """
    Vue qui permet d'afficher la convention de partenariat de perm d'id {id}.
    On récupère les informations en méthode de l'objet, et on va ensuite juste
    traiter la template et la render.
    """
    creneau = perm_models.Creneau.objects.get(pk=id)
    serializer = perm_serializers.CreneauSerializer(creneau)
    info = creneau.get_convention_information()
    logo_url = APP_URL + "/static/logo_monochrome.png"
    return render(request, 'convention.html',
                  {'creneau': serializer.data, 'articles': info['creneau_articles'], 'date': info["date"],
                   'montant': round(creneau.get_montant_deco_max(), 2), 'period': info['period'], 'logo_url': logo_url})


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def get_all_conventions(request):
    """
    Vue qui permet d'obtenir un pdf des conventions des assos d'un semestre
    Construit des fichiers pdf à partir d'un html pour chaque créneau tenu par une asso
    Puis merge le tout dans un géant pdf
    """
    semester_wanted = request.GET.get("semestre", False)
    if semester_wanted != False and int(semester_wanted) > 0:
        semestre_id = semester_wanted
    else :
        semestre_id = get_current_semester()
    queryset = perm_models.Creneau.objects.filter(perm__asso=True, perm__semestre__id=semestre_id)

    filenames = []

    for creneau in queryset:
        if creneau.article_set.exists():
            info = creneau.get_convention_information()
            serializer = perm_serializers.CreneauSerializer(creneau)
            logo_url = APP_URL + "/static/logo_monochrome.png"
            html_page = render_to_string('convention.html',
                        {'creneau': serializer.data, 'articles': info['creneau_articles'], 'date': info["date"],
                        'montant': round(creneau.get_montant_deco_max(), 2), 'period': info['period'], 'logo_url': logo_url})

            filename = 'convention_creneau_id_' + str(serializer.data["id"]) + '.pdf'
            pdf= pdfkit.from_string(html_page, filename)
            filenames.append(filename)

    merger = PdfFileMerger()
    for filename in filenames:
        f = open(filename, 'rb')
        input = PdfFileReader(f)
        merger.append(input, import_bookmarks=False)
        f.close()
    for filename in filenames:
        os.remove(filename)

    response = HttpResponse(content_type='application/pdf')
    merger.write(response)
    merger.close()
    return response


def excel_facture_generation(request):
    # Vue permettant de générer un fichier excel avec la liste des factures, et des perms associées
    response = HttpResponse(content_type='application/vnd.ms-excel; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Picasso_factures_recues.xls"'

    writer = Workbook(encoding="utf-8")
    ws = writer.add_sheet('Factures reçues')
    excel_dump = excel_generation.generate_receipts_xls(ws)
    writer.save(response)
    return response