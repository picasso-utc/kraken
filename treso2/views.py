from django.shortcuts import render
from rest_framework import viewsets
from treso2 import serializers as treso2_serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as status
from core import models as core_models
from treso2 import models as treso2_models
from core.services.payutc import PayutcClient
from django.http import JsonResponse, HttpResponse
from core.permissions import IsAdminUser
from xlwt import Workbook
from core.services import excel_generation

# Create your views here.
@permission_classes((IsAdminUser,))
class CategorieFactureRecueViewSet(viewsets.ModelViewSet):
    serializer_class = treso2_serializers.CategorieFactureRecueSerializer
    queryset = treso2_models.CategorieFactureRecue.objects.all()

@permission_classes((IsAdminUser,))
class FactureRecueViewSet(viewsets.ModelViewSet):
    serializer_class = treso2_serializers.FactureRecueSerializer
    queryset = treso2_models.FactureRecue.objects.all()

    def destroy(self, request, *args, **kwargs):
        facture = self.get_object()
        treso2_models.SuivieModificationFacture.objects.create(facuture_number=facture.facture_number, action='S', login=request.session.get('login'))
        facture.delete()
        return Response({'message':'Suppretion bien éffectué'})

    def update(self, request, *args, **kwargs):
        facture = self.get_object()
        treso2_models.SuivieModificationFacture.objects.create(facuture_number=facture.facture_number, action='M', login=request.session.get('login'))
        serializer = treso2_serializers.FactureRecueSerializer(instance=facture, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = treso2_serializers.FactureRecueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            treso2_models.SuivieModificationFacture.objects.create(facuture_number=serializer.data['facture_number'], action='C', login=request.session.get('login'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes((IsAdminUser,))
class FactureEmiseViewSet(viewsets.ModelViewSet):
    serializer_class = treso2_serializers.FactureEmiseSerializer
    queryset = treso2_models.FactureEmise.objects.all()

@permission_classes((IsAdminUser,))
class ChequeViewSet(viewsets.ModelViewSet):
    serializer_class = treso2_serializers.ChequeSerializer
    queryset = treso2_models.Cheque.objects.all()

@api_view(['GET'])
@permission_classes((IsAdminUser,))
def tva_info(request,id):
    """Obtention des informations de la tva"""

    # On recupère la periode dans laquelle on veut les infos sur la TVA
    periode = core_models.PeriodeTVA.objects.get(pk=id)

    # TVA déductible: TVA total sur les factures recues lors de cette periode
    facture_recues=treso2_models.FactureRecue.objects.filter(date__gte=periode.debut, date__lte=periode.fin)
    tva_deductible = list()
    tva_types = set(facture.tva for facture in facture_recues)
    for tva_type in tva_types:
        tva_deductible.append({'pourcentage':tva_type,
                               'montant': sum(
                                   facture.get_total_taxes for facture in facture_recues
                                   if facture.tva==tva_type)}
        )

    # Pour la TVA à déclarer :
    #   * On récupère toute la TVA sur PayUTC pendant cette période.
    #   * On récupère toute la TVA sur les factures émises pendant cette période.
    # Event_id hardcoded to 1

    # Recupèrer les ventes payut pendant la periode
    sessionid = request.session['payutc_session']
    p = PayutcClient(sessionid)
    sales = p.get_export(start=periode.debut.isoformat(), end=periode.fin.isoformat(), event_id=1)

    # Recupère les types de TVA (5.5%, 10%, 20% ...)
    payutc_tva_types = set(sale['pur_tva'] for sale in sales)

    # Recupère les factures emises pendant cette periode et chercher les differents types de TVA qu'ils contienent (Si il y en a)
    factures_emises = treso2_models.FactureEmise.objects.filter(date_creation__gte=periode.debut, date_creation__lte=periode.fin)
    tva_types = payutc_tva_types.union(set(facture.tva for facture in factures_emises))

    tva_a_declarer = list()
    for tva_type in tva_types:
        tva_a_declarer.append({'pourcentage': tva_type,
                               'montant': sum(
                                   [(1 - (100 / (100 + sale['pur_tva']))) * sale['total'] * 0.01 for sale in sales if
                                    sale['pur_tva'] == tva_type])
                                          +sum(
                                    facture.get_total_taxes for facture in factures_emises if facture.tva == tva_type)
        })

    return JsonResponse({'tva_deductible': tva_deductible,
                         'tva_a_declarer': tva_a_declarer,
                         'tva_a_declarer_total': sum(tva['montant'] for tva in tva_a_declarer)})

@api_view(['GET'])
@permission_classes((IsAdminUser,))
def facture_by_filter(request, idsemestre, idcategorie):
    facture_avec_criteres = list()
    if (idsemestre==0):
        factures = treso2_models.FactureRecue.objects.all()
        for facture in factures:
            facture_avec_criteres.append(treso2_serializers.FactureRecueSerializer(instance=facture).data)
            return JsonResponse(facture_avec_criteres, safe=False)

    factures = treso2_models.FactureRecue.objects.filter(semestre=idsemestre)
    if (idcategorie==0):
        for facture in factures:
            facture_avec_criteres.append(treso2_serializers.FactureRecueSerializer(instance=facture).data)
    else:
        categorie = treso2_models.CategorieFactureRecue.objects.get(pk=idcategorie)
        relation_DB = treso2_models.CategoriePrix.objects.filter(categorie=categorie)
        for categorie_prix in relation_DB:
            if (factures.filter(pk=categorie_prix.facture.id).exists()):
                facture_id = categorie_prix.facture
                facture_avec_criteres.append(treso2_serializers.FactureRecueSerializer(instance=facture_id).data)

    return JsonResponse(facture_avec_criteres, safe=False)

@api_view(['POST'])
@permission_classes((IsAdminUser,))
def categorie_stats(request):
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    factures = treso2_models.FactureRecue.objects.filter(date__gte=start_date, date__lte=end_date)

    categorie_sum_total = {}
    sous_categorie_sum_total = {}
    for facture in factures:
        relation_DB = treso2_models.CategoriePrix.objects.filter(facture=facture)
        for categorie_prix in relation_DB:
            categorie_sum_total[categorie_prix.categorie.id] = categorie_sum_total.get(categorie_prix.categorie.id,0)+categorie_prix.prix
        relation_DB = treso2_models.SousCategoriePrix.objects.filter(facture=facture)
        for sous_categorie_prix in relation_DB:
            sous_categorie_sum_total[sous_categorie_prix.sous_categorie.id] = sous_categorie_sum_total.get(sous_categorie_prix.sous_categorie.id,0)+sous_categorie_prix.prix
    for key in sous_categorie_sum_total.keys():
        categorie_id = treso2_models.SousCategorieFactureRecue.objects.get(pk=key).categorie.id
        if (isinstance(categorie_sum_total[categorie_id],dict)):
            categorie_sum_total[categorie_id]['sous_categories'][key] = sous_categorie_sum_total[key]
        else:
            categorie_sum_total[categorie_id]={'total': categorie_sum_total[categorie_id], 'sous_categories':{key : sous_categorie_sum_total[key]}}

    for key in categorie_sum_total.keys():
        if (not isinstance(categorie_sum_total[key],dict)):
            categorie_sum_total[key] = {'total': categorie_sum_total[key]}

    return JsonResponse(categorie_sum_total,safe=False)

@api_view(['GET'])
@permission_classes((IsAdminUser,))
def excel_facture_generation(request, idsemestre, idcategorie):
    # Vue permettant de générer un fichier excel avec la liste des factures, et des perms associées
    response = HttpResponse(content_type='application/vnd.ms-excel; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Picasso_factures_recues.xls"'

    writer = Workbook(encoding="utf-8")
    ws = writer.add_sheet('Factures reçues')

    facture_avec_criteres = list()
    factures = treso2_models.FactureRecue.objects.filter(semestre=idsemestre).order_by('date_created')
    if (idcategorie == 0):
        for facture in factures:
            facture_avec_criteres.append(facture)
    else:
        categorie = treso2_models.CategorieFactureRecue.objects.get(pk=idcategorie)
        relation_DB = treso2_models.CategoriePrix.objects.filter(categorie=categorie)
        for categorie_prix in relation_DB:
            if (factures.filter(pk=categorie_prix.facture.id).exists()):
                facture_id = categorie_prix.facture
                facture_avec_criteres.append(facture_id)

    excel_dump = excel_generation.generate_facture_xls(worksheet=ws,factures=facture_avec_criteres)
    writer.save(response)
    return response


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def excel_cheque_generation(request):
    # Vue permettant de générer un fichier excel avec la liste des chèques
    response = HttpResponse(content_type='application/vnd.ms-excel; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="Picasso_cheques_recues.xls"'

    writer = Workbook(encoding="utf-8")
    ws = writer.add_sheet('Chèques')
    excel_dump = excel_generation.generate_cheque_xls(ws)
    writer.save(response)
    return response