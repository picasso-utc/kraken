import datetime
import os
from datetime import datetime, timedelta

import pdfkit
from PyPDF2 import PdfFileMerger, PdfFileReader
from constance import config
from django.core.mail import EmailMessage
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, permission_classes

from core.permissions import IsAuthenticatedUser, IsMemberUser, CanAccessMenuFunctionnalities, HasApplicationRight
from core.services.current_semester import get_current_semester, get_request_semester
from core.services.portal import PortalClient
from core.settings import DEFAULT_FROM_EMAIL
from core.settings import FRONT_URL
from tv import models as tv_models
from . import models as perm_models
from . import serializers as perm_serializers


class PermViewSet(viewsets.ModelViewSet):
    """ViewSet des perms"""
    serializer_class = perm_serializers.PermSerializer
    permission_classes = (IsMemberUser,)

    def get_queryset(self):
        qs = perm_models.Perm.objects
        return get_request_semester(qs, self.request)


class CreneauViewSet(viewsets.ModelViewSet):
    """ViewSet des créneaux"""
    serializer_class = perm_serializers.CreneauSerializer
    permission_classes = (IsMemberUser,)

    def get_queryset(self):
        qs = perm_models.Creneau.objects
        return get_request_semester(qs, self.request, "perm__semestre__id")


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_creneau_sales(request, id):
    """Obtenir les ventes d'un créneau"""
    c = perm_models.Creneau.objects.get(pk=id)
    return JsonResponse(c.get_justificatif_information())


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.ArticleSerializer
    queryset = perm_models.Article.objects.all()
    permission_classes = (IsMemberUser,)


class AstreinteViewSet(viewsets.ModelViewSet):
    """ViewSet Astreinte"""
    serializer_class = perm_serializers.AstreinteSerializer
    permission_classes = (IsMemberUser,)

    def get_queryset(self):
        qs = perm_models.Astreinte.objects
        return get_request_semester(qs, self.request, "member__semestre__id")


class MenuViewSet(viewsets.ModelViewSet):
    """
    Menu viewset
    """
    permission_classes = (CanAccessMenuFunctionnalities,)
    queryset = perm_models.Menu.objects.filter(is_closed=False)
    serializer_class = perm_serializers.MenuSerializer


class SignatureViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ViewwSet des signatures de charte"""
    serializer_class = perm_serializers.SignatureSerializer
    queryset = perm_models.Signature.objects.all()


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def create_payutc_article(request, id):
    """
        Permet d'obtenir, pour un article de pk {id}, d'enregistrer l'article dans PayUTC.
        On met les TV sur Menu après création
    """
    article = perm_models.Article.objects.get(pk=id)
    article.create_payutc_article()

    # Put Menu Link for tvs, id = 3
    tv_1 = tv_models.WebTV.objects.get(pk=1)
    tv_2 = tv_models.WebTV.objects.get(pk=2)
    menu_link = tv_models.WebTVLink.objects.get(pk=3)
    tv_1.link = menu_link
    tv_1.save()
    tv_2.link = menu_link
    tv_2.save()

    return JsonResponse({})


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_article_sales(request, id):
    """Permet d'obtenir, pour un article de pk {id}, le nombre de ventes."""
    article = perm_models.Article.objects.get(pk=id)
    sales = article.update_sales()
    return JsonResponse({'sales': sales})


def get_creneau(date):
    """Déterminer si la perm en cours est celle du matin, du midi ou du soir"""
    hour = date.time().hour
    if hour >= 16:
        return 'S'
    elif hour >= 11:
        return 'D'
    return 'M'


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_current_creneau(request):
    """Obtenir le créneau en cours"""
    date = datetime.now()
    creneau = get_creneau(date)
    queryset = perm_models.Creneau.objects.filter(creneau=creneau, date=date)
    serializer = perm_serializers.CreneauSerializer(queryset, many=True)
    current_creneau = dict()
    if serializer.data:
        current_creneau = serializer.data[0]
    return JsonResponse(current_creneau)


@api_view(['GET'])
def get_current_public_creneau(request):
    """Obtenir le créneau en cours (sans être authentifié)"""
    date = datetime.now()
    creneau = get_creneau(date)

    queryset = perm_models.Creneau.objects.filter(creneau=creneau, date=date)
    serializer = perm_serializers.CreneauPublicSerializer(queryset, many=True)
    current_creneau = dict()
    if serializer.data:
        current_creneau = serializer.data[0]
    return JsonResponse(current_creneau)


@api_view(['GET'])
@permission_classes((CanAccessMenuFunctionnalities,))
def get_order_lines(request, id):
    """Obtenir les commandes pour un menu à partir de l'id de l'article"""
    menu = perm_models.Menu.objects.get(article__id_payutc=id)
    orders = perm_models.Menu.update_orders(menu)
    orderlines = perm_models.OrderLine.objects.filter(menu__article__id_payutc=id, is_canceled=False, quantity__gt=0)
    total_quantity = sum(order.quantity for order in orderlines)
    orderlines_served = orderlines.filter(served=True)
    served_quantity = sum(order.quantity for order in orderlines_served)
    return JsonResponse({
        'menu': {'name': menu.article.nom, 'quantity': menu.article.stock, 'id_payutc': id,
                 'total_quantity': total_quantity,
                 'served_quantity': served_quantity},
        'orders': orders
    })


@api_view(['POST'])
@permission_classes((CanAccessMenuFunctionnalities,))
def set_ordeline_served(request, id):
    """
    Permet de dire qu'un menu a été donné.
    """
    orderline = perm_models.OrderLine.objects.get(id_transaction_payutc=id)
    if orderline.served:
        orderline.served = False
    else:
        orderline.served = True
    orderline.save()
    return JsonResponse({})


@api_view(['POST'])
@permission_classes((CanAccessMenuFunctionnalities,))
def set_ordeline_staff(request, id):
    """
    Permet de dire qu'un menu doit être reporté ou non reporté s'il l'est déjà.
    """
    orderline = perm_models.OrderLine.objects.get(id_transaction_payutc=id)
    if orderline.is_staff:
        orderline.is_staff = False
    else:
        orderline.is_staff = True
    orderline.save()
    return JsonResponse({})


@api_view(['POST'])
@permission_classes((CanAccessMenuFunctionnalities,))
def set_menu_closed(request, id):
    """
    Ferme le menu
    Article du menu désactivé sur Weez
    Remet les télés sur l'url par défaut
    """
    menu = perm_models.Menu.objects.get(article__id_payutc=id)
    if menu.is_closed:
        menu.is_closed = False
    else:

        menu.article.set_article_disabled()
        menu.is_closed = True
    menu.save()
    # Put Default Link for tvs, id = 4
    tv_1 = tv_models.WebTV.objects.get(pk=1)
    tv_2 = tv_models.WebTV.objects.get(pk=2)
    default_link = tv_models.WebTVLink.objects.get(pk=4)
    tv_1.link = default_link
    tv_1.save()
    tv_2.link = default_link
    tv_2.save()
    return JsonResponse({})


@api_view(['POST'])
@permission_classes((IsMemberUser,))
def send_mail(request):
    """
    Envoie l'email d'annonce des perms à toutes les perms de la requête
    """
    perms = request.data
    for perm in perms:
        creneaux = []
        for creneau in perm["creneaux"]:
            creneau_information = creneau.split(":")
            date_information = creneau_information[0].split("-")
            date = date_information[2] + "/" + date_information[1] + "/" + date_information[0]

            creneau_type = "Soir"
            creneau_index = 2
            if creneau_information[1] == "D":
                creneau_type = "Midi"
                creneau_index = 1
            elif creneau_information[1] == "M":
                creneau_type = "Matin"
                creneau_index = 0

            new_creneau = {'date': date, 'creneau_type': creneau_type, 'creneau_index': creneau_index}
            creneaux.append(new_creneau)

        sorted_creneaux = sorted(creneaux, key=lambda x: x['creneau_index'])

        mail_content = render_to_string('perm_notification.html', {'creneaux': sorted_creneaux})
        email = EmailMessage(
            subject=f"Pic'Asso - Perm {perm['nom']}",
            body=mail_content,
            from_email=DEFAULT_FROM_EMAIL,
            to=[perm['mail_resp']],
        )
        email.content_subtype = "html"  # this is the crucial part
        email.attach_file('core/templates/exemple_planning.xlsx')
        email.send()
        print(f"Envoi du mail {perm['nom']}")

    return JsonResponse({})


@api_view(['GET'])
@permission_classes((HasApplicationRight,))
def send_creneau_reminder(request):
    """Envoi un mail de rappel aux créneaux ayant lieu dans 7 jours"""
    # Search for date in one week
    reminder_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    # Search in database creneau that fit this date
    queryset = perm_models.Creneau.objects.filter(date=reminder_date)
    serializer = perm_serializers.CreneauSerializer(queryset, many=True)

    creneaux = serializer.data
    for creneau in creneaux:
        date_information = creneau["date"].split("-")
        date = date_information[2] + "/" + date_information[1] + "/" + date_information[0]

        mail_content = render_to_string('perm_reminder.html', {'creneau_type': creneau['creneau']})
        email = EmailMessage(
            subject=f"Pic'Asso - Perm {creneau['perm']['nom']} - {date}",
            body=mail_content,
            from_email=DEFAULT_FROM_EMAIL,
            to=[creneau['perm']['mail_resp']],
        )
        email.content_subtype = "html"  # this is the crucial part
        if creneau['creneau'] == 'S':
            email.attach_file('core/templates/exemple_planning.xlsx')
        email.send()

    return JsonResponse({})


@api_view(['POST'])
def get_week_calendar(request):
    """Obtenir le calendrier publique entre les dates envoyées en paramètre"""
    data = request.data
    queryset = perm_models.Creneau.objects.filter(date__range=(data['start_date'], data['end_date']))
    serializer = perm_serializers.CreneauPublicSerializer(queryset, many=True)
    return JsonResponse({'creneaux': serializer.data})


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_user_astreintes(request):
    """Obtenir les astreintes d'un membre du Pic"""
    member_id = request.session.get('member_id')

    if member_id:
        print(member_id)
        astreinte_queryset = perm_models.Astreinte.objects.filter(member_id=member_id)
        astreintes = perm_serializers.AstreinteSerializer(astreinte_queryset, many=True)

        return JsonResponse({'astreintes': astreintes.data})

    return JsonResponse({'astreintes': []})


@api_view(['POST'])
@permission_classes((IsMemberUser,))
def get_week_astreintes(request):
    """
    Obtenir les créneaux entre deux dates entrées en paramètre
    avec astreintes enregistrées sur chaque créneau
    """
    data = request.data
    queryset = perm_models.Creneau.objects.filter(date__range=(data['start_date'], data['end_date']))
    serializer = perm_serializers.CreneauAstreinteSerializer(queryset, many=True)
    return JsonResponse({'creneaux': serializer.data})


class PermHalloweenViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.PermHalloweenSerializer
    queryset = perm_models.PermHalloween.objects.all()
    # permission_classes = (IsAdminUser,)


@api_view(['GET'])
# @permission_classes((IsMemberUser, ))
def get_halloween_article_count(request):
    """Compte le nb d'enregistrement dans PermHalloween pour un article_id"""
    article_id = request.GET.get("article_id", 1)
    queryset = perm_models.PermHalloween.objects.filter(article_id=article_id)
    return JsonResponse({'count': len(queryset)})


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_creaneau_signature(request, creneau_id):
    """Obtenir le nombre de signature pour un créneau donné"""
    queryset = perm_models.Signature.objects.filter(creneau__id=creneau_id)
    return JsonResponse({'signature_count': len(queryset)})


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_perms_for_notation(request):
    """Obtenir les notation de toutes les perms du semestre entré (courant par défaut)"""
    qs = perm_models.Creneau.objects
    queryset = get_request_semester(qs, request, "perm__semestre__id")
    serializer = perm_serializers.CreneauSerializer(queryset, many=True)

    creneaux = serializer.data
    perms = dict()

    for creneau in creneaux:

        perm_id = creneau["perm"]["id"]

        if perm_id not in perms:
            perms[perm_id] = {}
            perms[perm_id] = creneau["perm"]
            perms[perm_id].pop("creneaux")
            perms[perm_id]["creneau"] = []
            perms[perm_id]["note_deco"] = 0
            perms[perm_id]["note_anim"] = 0
            perms[perm_id]["note_orga"] = 0
            perms[perm_id]["note_menu"] = 0
            perms[perm_id]["nb_note_deco"] = 0
            perms[perm_id]["nb_note_anim"] = 0
            perms[perm_id]["nb_note_orga"] = 0
            perms[perm_id]["nb_note_menu"] = 0
            perms[perm_id]["nb_astreintes"] = 0

        if not any(c for c in perms[perm_id]["creneau"] if c["id"] == creneau["id"]):
            creneau_data = creneau
            creneau_data.pop("perm")
            creneau_data.pop("state")
            creneau_data.pop("montantTTCMaxAutorise")
            creneau_data.pop('facturerecue_set')
            creneau_data["notation"] = []
            perms[perm_id]["creneau"].append(creneau_data)

    qs = perm_models.Astreinte.objects
    queryset = get_request_semester(qs, request, "member__semestre__id")
    serializer = perm_serializers.AstreinteSerializer(queryset, many=True)

    astreintes = serializer.data

    for astreinte in astreintes:
        perm_id = astreinte["creneau"]["perm"]["id"]

        if perm_id in perms:

            notation = {
                "astreinte_type": astreinte["astreinte_type"],
                "note_deco": astreinte["note_deco"],
                "note_orga": astreinte["note_orga"],
                "note_anim": astreinte["note_anim"],
                "note_menu": astreinte["note_menu"],
                "commentaire": astreinte["commentaire"]
            }

            if astreinte["note_deco"] > 0:
                perms[perm_id]["note_deco"] += astreinte["note_deco"]
                perms[perm_id]["nb_note_deco"] += 1
            if astreinte["note_anim"] > 0:
                perms[perm_id]["note_anim"] += astreinte["note_anim"]
                perms[perm_id]["nb_note_anim"] += 1
            if astreinte["note_orga"] > 0:
                perms[perm_id]["note_orga"] += astreinte["note_orga"]
                perms[perm_id]["nb_note_orga"] += 1
            if astreinte["note_menu"] > 0:
                perms[perm_id]["note_menu"] += astreinte["note_menu"]
                perms[perm_id]["nb_note_menu"] += 1
            perms[perm_id]["nb_astreintes"] += 1

            for creneau in perms[perm_id]["creneau"]:
                if creneau["id"] == astreinte["creneau"]["id"]:
                    creneau["notation"].append(notation)
                    break

    keys = perms.keys()
    for key in keys:

        # Obtenir la moyenne générale
        mean_note = 0
        mean_keys = 0

        if perms[key]["nb_note_deco"] > 0:
            perms[key]["note_deco"] = round(perms[key]["note_deco"] / perms[key]["nb_note_deco"], 2)
            mean_note += perms[key]["note_deco"]
            mean_keys += 1
        if perms[key]["nb_note_menu"] > 0:
            perms[key]["note_menu"] = round(perms[key]["note_menu"] / perms[key]["nb_note_menu"], 2)
            mean_note += perms[key]["note_menu"]
            mean_keys += 1
        if perms[key]["nb_note_orga"] > 0:
            perms[key]["note_orga"] = round(perms[key]["note_orga"] / perms[key]["nb_note_orga"], 2)
            mean_note += perms[key]["note_orga"]
            mean_keys += 1
        if perms[key]["nb_note_anim"] > 0:
            perms[key]["note_anim"] = round(perms[key]["note_anim"] / perms[key]["nb_note_anim"], 2)
            mean_note += perms[key]["note_anim"]
            mean_keys += 1

        if mean_keys > 0:
            mean_note = round(mean_note / mean_keys, 2)
        perms[key]["mean_note"] = mean_note

    return JsonResponse({'perms': list(perms.values())})


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_perm_for_notation(request, perm_id):
    """Obtenir les informations de notation d'une perm entrée en paramètre"""

    queryset = perm_models.Creneau.objects.filter(perm__id=perm_id)
    serializer = perm_serializers.CreneauSerializer(queryset, many=True)

    creneaux = serializer.data

    perm = dict()

    for creneau in creneaux:

        if "creneau" not in perm:
            perm = creneau["perm"]
            perm.pop("creneaux")
            perm["creneau"] = []
            perm["note_deco"] = 0
            perm["note_anim"] = 0
            perm["note_orga"] = 0
            perm["note_menu"] = 0
            perm["mean_m"] = 0
            perm["mean_d"] = 0
            perm["mean_s"] = 0
            perm["nb_note_deco"] = 0
            perm["nb_note_anim"] = 0
            perm["nb_note_orga"] = 0
            perm["nb_note_menu"] = 0
            perm["nb_astreintes"] = 0
            perm["nb_note_m"] = 0
            perm["nb_note_d"] = 0
            perm["nb_note_s"] = 0

        if not any(c for c in perm["creneau"] if c["id"] == creneau["id"]):
            creneau_data = creneau
            creneau_data.pop("perm")
            creneau_data.pop("state")
            creneau_data.pop("montantTTCMaxAutorise")
            creneau_data.pop('facturerecue_set')
            creneau_data["notation"] = []
            perm["creneau"].append(creneau_data)

    if "id" in perm:

        queryset = perm_models.Astreinte.objects.filter(creneau__perm__id=perm_id)
        serializer = perm_serializers.AstreinteSerializer(queryset, many=True)

        creneau_keys = {
            'M': ('mean_m', 'nb_note_m'),
            'D': ('mean_d', 'nb_note_d'),
            'S': ('mean_s', 'nb_note_s')
        }

        astreintes = serializer.data

        for astreinte in astreintes:

            if perm_id == astreinte["creneau"]["perm"]["id"]:

                notation = {
                    "astreinte_type": astreinte["astreinte_type"],
                    "note_deco": astreinte["note_deco"],
                    "note_orga": astreinte["note_orga"],
                    "note_anim": astreinte["note_anim"],
                    "note_menu": astreinte["note_menu"],
                    "commentaire": astreinte["commentaire"]
                }

                if astreinte["note_deco"] > 0:
                    perm["note_deco"] += astreinte["note_deco"]
                    perm["nb_note_deco"] += 1
                    perm[creneau_keys[astreinte["creneau"]["creneau"]][0]] += astreinte["note_deco"]
                    perm[creneau_keys[astreinte["creneau"]["creneau"]][1]] += 1
                if astreinte["note_anim"] > 0:
                    perm["note_anim"] += astreinte["note_anim"]
                    perm["nb_note_anim"] += 1
                    perm[creneau_keys[astreinte["creneau"]["creneau"]][0]] += astreinte["note_anim"]
                    perm[creneau_keys[astreinte["creneau"]["creneau"]][1]] += 1
                if astreinte["note_orga"] > 0:
                    perm["note_orga"] += astreinte["note_orga"]
                    perm["nb_note_orga"] += 1
                    perm[creneau_keys[astreinte["creneau"]["creneau"]][0]] += astreinte["note_orga"]
                    perm[creneau_keys[astreinte["creneau"]["creneau"]][1]] += 1
                if astreinte["note_menu"] > 0:
                    perm["note_menu"] += astreinte["note_menu"]
                    perm["nb_note_menu"] += 1
                    perm[creneau_keys[astreinte["creneau"]["creneau"]][0]] += astreinte["note_menu"]
                    perm[creneau_keys[astreinte["creneau"]["creneau"]][1]] += 1
                perm["nb_astreintes"] += 1

                for creneau in perm["creneau"]:
                    if creneau["id"] == astreinte["creneau"]["id"]:
                        creneau["notation"].append(notation)
                        break

        if perm["nb_note_m"] > 0:
            perm["mean_m"] = round(perm["mean_m"] / perm["nb_note_m"], 2)
        else:
            perm["mean_m"] = None
        if perm["nb_note_d"] > 0:
            perm["mean_d"] = round(perm["mean_d"] / perm["nb_note_d"], 2)
        else:
            perm["mean_d"] = None
        if perm["nb_note_s"] > 0:
            perm["mean_s"] = round(perm["mean_s"] / perm["nb_note_s"], 2)
        else:
            perm["mean_s"] = None

        if perm["nb_note_deco"] > 0:
            perm["note_deco"] = round(perm["note_deco"] / perm["nb_note_deco"], 2)
        if perm["nb_note_menu"] > 0:
            perm["note_menu"] = round(perm["note_menu"] / perm["nb_note_menu"], 2)
        if perm["nb_note_orga"] > 0:
            perm["note_orga"] = round(perm["note_orga"] / perm["nb_note_orga"], 2)
        if perm["nb_note_anim"] > 0:
            perm["note_anim"] = round(perm["note_anim"] / perm["nb_note_anim"], 2)

        return JsonResponse(perm)

    else:
        return JsonResponse({})


@api_view(['GET'])
def perm_may_be_requested(request):
    """Retourne si les demandes de perm sont activées"""
    return JsonResponse({'perm_may_be_requested': config.__getattr__('PERM_MAY_BE_REQUESTED')})


@api_view(['POST'])
@permission_classes((IsMemberUser,))
def update_perm_may_be_requested_setting(request):
    """Mets à jour le paramètre d'activation des demandes de perm"""
    if 'perm_may_be_requested' in request.data:
        perm_may_be_requested = request.data['perm_may_be_requested']
        config.__setattr__('PERM_MAY_BE_REQUESTED', perm_may_be_requested)
    return JsonResponse({})


# A revoir pour le semestre courant
def retrieve(request, pk=None):
    requested_perm = perm_models.RequestedPerm.objects.get(pk=pk)
    serializer = perm_serializers.RequestedPermSerializer(requested_perm)

    # Check if the user is the founder of the requested_perm object
    login = request.session.get('login')
    if login == serializer.data["founder_login"]:
        return JsonResponse({'perm': serializer.data})

    return JsonResponse({"error": "Vous n'avez pas la permission d'accéder à cette ressource"}, status=403)


class RequestedPermViewSet(viewsets.ViewSet):
    """ViewSet à la mano des perms demandées"""

    @staticmethod
    def list(request):
        queryset = perm_models.RequestedPerm.objects.filter(semestre__id=get_current_semester())
        serializer = perm_serializers.RequestedPermSerializer(queryset, many=True)

        return JsonResponse({'requested_perms': serializer.data})

    def create(self, request):
        if not self.perm_may_be_requested():
            return JsonResponse({'error': 'Il n\'est pas possible de demander une perm.'})
        serializer = perm_serializers.RequestedPermSerializer(request.data)
        requested_perm = serializer.data
        new_requested_perm = perm_models.RequestedPerm.objects.create(
            nom=requested_perm["nom"],
            asso=requested_perm["asso"],
            mail_asso=requested_perm["mail_asso"],
            nom_resp=requested_perm["nom_resp"],
            mail_resp=requested_perm["mail_resp"],
            nom_resp_2=requested_perm["nom_resp_2"],
            mail_resp_2=requested_perm["mail_resp_2"],
            theme=requested_perm["theme"],
            description=requested_perm["description"],
            membres=requested_perm["membres"],
            founder_login=requested_perm["founder_login"],
            ambiance=requested_perm["ambiance"],
            periode=requested_perm["periode"]
        )

        url = FRONT_URL + "/perm/form?form_id=" + str(new_requested_perm.pk)
        mail_content = "Coucou,\n\n" \
                       + "Ta demande de perm " + requested_perm[
                           "nom"] + " a bien été enregistrée. Tu peux la modifier ici : \n" \
                       + url + "\n\n" \
                       + "La bise, et à bientôt au Pic'Asso !"
        email = EmailMessage(
            subject=f"Pic'Asso - Demande de perm",
            body=mail_content,
            from_email=DEFAULT_FROM_EMAIL,
            to=[requested_perm["mail_resp"]],
        )
        email.send()

        return JsonResponse({"id": new_requested_perm.pk})

    def update(self, request, pk=None):
        if not self.perm_may_be_requested():
            return JsonResponse({'error': 'Il n\'est pas possible de mettre à jour une perm.'})
        requested_perm = perm_models.RequestedPerm.objects.get(pk=pk)

        # Check if the user is the founder of the requested_perm object
        login = request.session.get('login')
        if login != requested_perm.founder_login:
            return JsonResponse({"error": "Vous n'avez pas la permission d'accéder à cette ressource"}, status=403)

        requested_perm.nom = request.data["nom"]
        requested_perm.asso = request.data["asso"]
        requested_perm.mail_asso = request.data["mail_asso"]
        requested_perm.nom_resp = request.data["nom_resp"]
        requested_perm.mail_resp = request.data["mail_resp"]
        requested_perm.nom_resp_2 = request.data["nom_resp_2"]
        requested_perm.mail_resp_2 = request.data["mail_resp_2"]
        requested_perm.theme = request.data["theme"]
        requested_perm.description = request.data["description"]
        requested_perm.membres = request.data["membres"]
        requested_perm.ambiance = request.data["ambiance"]
        requested_perm.periode = request.data["periode"]
        requested_perm.save(update_fields=[
            'nom', 'asso', 'mail_asso', 'nom_resp', 'mail_resp', 'nom_resp_2', 'mail_resp_2', 'theme', 'description',
            'membres', 'founder_login',
            'ambiance', 'periode'
        ])
        return JsonResponse({})

    @staticmethod
    def partial_update(request, pk=None):
        requested_perm = perm_models.RequestedPerm.objects.get(pk=pk)
        requested_perm.added = not requested_perm.added
        requested_perm.save()
        return JsonResponse({})

    @staticmethod
    def perm_may_be_requested():
        return config.__getattr__('PERM_MAY_BE_REQUESTED')

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'partial_update':
            permission_classes = [IsMemberUser]
        else:
            permission_classes = [IsAuthenticatedUser]
        return [permission() for permission in permission_classes]


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_pdf_requested_perms(request):
    """Obtenir un giga PDF des perms demandées"""
    queryset = perm_models.RequestedPerm.objects.filter(semestre__id=get_current_semester())
    serializer = perm_serializers.RequestedPermSerializer(queryset, many=True)

    filenames = []
    for requested_perm in serializer.data:
        html_page = render_to_string('requested_perm.html', {'requested_perm': requested_perm})
        filename = 'requested_perm_id_' + str(requested_perm["id"]) + '.pdf'
        pdf = pdfkit.from_string(html_page, filename)
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


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser,))
def get_portal_assos(request):
    """Obtenir les associations de l'UTC via le Portail des assos"""
    p = PortalClient()
    response = p.get_assos()
    return JsonResponse({'assos': response['data']}, status=response['status'])
