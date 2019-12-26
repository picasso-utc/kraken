from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, mixins
from . import serializers as perm_serializers
from django.template.loader import get_template, render_to_string
from .import models as perm_models
from django.shortcuts import render
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, IsMemberUserOrReadOnly, CanAccessMenuFunctionnalities, HasApplicationRight
import datetime
from core.settings import DEFAULT_FROM_EMAIL
from django.core.mail import send_mail
from datetime import date, datetime, timedelta
from django.core.mail import EmailMessage
from tv import models as tv_models
from tv import serializers as tv_serializers
from constance import config
from core.settings import CONSTANCE_CONFIG
from core.services.current_semester import get_current_semester
from core.services.portal import PortalClient
from core.services.HtmlPdf import HtmlPdf


class PermViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.PermSerializer
    queryset = perm_models.Perm.objects.all()
    permission_classes = (IsMemberUser,)


class CreneauViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.CreneauSerializer
    queryset = perm_models.Creneau.objects.all()
    permission_classes = (IsMemberUser,)


@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def get_creneau_sales(request, id):
    c = perm_models.Creneau.objects.get(pk=id)
    return JsonResponse(c.get_justificatif_information())


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.ArticleSerializer
    queryset = perm_models.Article.objects.all()
    permission_classes = (IsMemberUser,)

class AstreinteViewSet(viewsets.ModelViewSet):
    serializer_class = perm_serializers.AstreinteSerializer
    queryset = perm_models.Astreinte.objects.all()
    permission_classes = (IsMemberUser,)

class MenuViewSet(viewsets.ModelViewSet):
    """
    Menu viewset
    """
    # TO DO Restreindre Méthode
    permission_classes = (CanAccessMenuFunctionnalities,)
    queryset = perm_models.Menu.objects.filter(is_closed=False)
    serializer_class = perm_serializers.MenuSerializer


class SignatureViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = perm_serializers.SignatureSerializer
    queryset = perm_models.Signature.objects.all()



@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def create_payutc_article(request, id):
    # Endpoint qui permet d'obtenir, pour un article de pk {id}, d'enregistrer l'article dans PayUTC.
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
@permission_classes((IsMemberUser, ))
def get_article_sales(request, id):
    # Endpoint qui permet d'obtenir, pour un article de pk {id}, le nombre de ventes.
    article = perm_models.Article.objects.get(pk=id)
    sales = article.update_sales()
    return JsonResponse({'sales': sales})


def get_creneau(date):

    # On déterminer si la perm en cours est celle du matin, du midi ou du soir
    hour = date.time().hour
    if hour >= 16 :
        return 'S'
    elif hour >= 11:
        return 'D'
    return 'M'

@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def get_current_creneau(request):
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
    date = datetime.now()
    creneau = get_creneau(date)
    
    queryset = perm_models.Creneau.objects.filter(creneau=creneau, date=date)
    serializer = perm_serializers.CreneauPublicSerializer(queryset, many=True)
    current_creneau = dict()
    if serializer.data:
        current_creneau = serializer.data[0]
    return JsonResponse(current_creneau)


@api_view(['GET'])
@permission_classes((CanAccessMenuFunctionnalities, ))
def get_order_lines(request, id):
    menu = perm_models.Menu.objects.get(article__id_payutc=id)
    orders = perm_models.Menu.update_orders(menu)
    orderlines = perm_models.OrderLine.objects.filter(menu__article__id_payutc=id, is_canceled=False, quantity__gt=0)
    total_quantity = sum(order.quantity for order in orderlines)
    orderlines_served = orderlines.filter(served=True)
    served_quantity = sum(order.quantity for order in orderlines_served)
    return JsonResponse({
        'menu': {'name': menu.article.nom, 'quantity': menu.article.stock, 'id_payutc': id, 'total_quantity': total_quantity,
                 'served_quantity': served_quantity},
        'orders': orders
    })



@api_view(['POST'])
@permission_classes((CanAccessMenuFunctionnalities, ))
def set_ordeline_served(request, id):
    """
    Endpoint qui permet de dire qu'un menu a été donné.
    """
    orderline = perm_models.OrderLine.objects.get(id_transaction_payutc=id)
    if orderline.served:
        orderline.served = False
    else:
        orderline.served = True
    orderline.save()
    return JsonResponse({})


@api_view(['POST'])
@permission_classes((CanAccessMenuFunctionnalities, ))
def set_ordeline_staff(request, id):
    """
    Endpoint qui permet de dire qu'un menu a été donné.
    """
    orderline = perm_models.OrderLine.objects.get(id_transaction_payutc=id)
    if orderline.is_staff:
        orderline.is_staff = False
    else:
        orderline.is_staff = True
    orderline.save()
    return JsonResponse({})


@api_view(['POST'])
@permission_classes((CanAccessMenuFunctionnalities, ))
def set_menu_closed(request, id):
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
@permission_classes((IsMemberUser, ))
def send_mail(request):
    
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

        # TO DO Sort creneaux
        sorted_creneaux = sorted(creneaux, key=lambda x: x['creneau_index'])

        mail_content = render_to_string('perm_notification.html', {'creneaux': sorted_creneaux})
        email = EmailMessage(
            subject=f"Pic'Asso - Perm {perm['nom']}",
            body=mail_content,
            from_email=DEFAULT_FROM_EMAIL,
            to=[perm['mail_resp']],
        )
        email.content_subtype = "html" # this is the crucial part 
        email.attach_file('core/templates/exemple_planning.xlsx')
        email.send()
        print(f"Envoi du mail {perm['nom']}")

    return JsonResponse({})


@api_view(['GET'])
@permission_classes((HasApplicationRight,))
def send_creneau_reminder(request):

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
        email.content_subtype = "html" # this is the crucial part 
        if creneau['creneau'] == 'S':
            email.attach_file('core/templates/exemple_planning.xlsx')
        email.send()

    return JsonResponse({})


@api_view(['POST'])
def get_week_calendar(request):

    data = request.data
    queryset = perm_models.Creneau.objects.filter(date__range=(data['start_date'], data['end_date']))
    serializer = perm_serializers.CreneauPublicSerializer(queryset, many=True)
    return JsonResponse({'creneaux': serializer.data})


@api_view(['GET'])
@permission_classes((IsMemberUser, ))
def get_user_astreintes(request):

    member_id = request.session.get('member_id')

    if member_id:
        print(member_id)
        astreinte_queryset = perm_models.Astreinte.objects.filter(member_id = member_id)
        astreintes = perm_serializers.AstreinteSerializer(astreinte_queryset, many = True)

        return JsonResponse({'astreintes': astreintes.data})

    return JsonResponse({'astreintes': []})


@api_view(['POST'])
@permission_classes((IsMemberUser, ))
def get_week_astreintes(request):

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

    article_id = request.GET.get("article_id", 1)
    queryset = perm_models.PermHalloween.objects.filter(article_id=article_id)
    return JsonResponse({'count': len(queryset)})


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_creaneau_signature(request, creneau_id):

    queryset = perm_models.Signature.objects.filter(creneau__id=creneau_id)
    return JsonResponse({'signature_count': len(queryset)})



@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_perms_for_notation(request):

    queryset = perm_models.Creneau.objects.all()
    serializer = perm_serializers.CreneauSerializer(queryset, many=True)

    creneaux = serializer.data

    perms = dict()

    for creneau in creneaux : 

        perm_id = creneau["perm"]["id"]

        if perm_id not in perms : 

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

    queryset = perm_models.Astreinte.objects.all()
    serializer = perm_serializers.AstreinteSerializer(queryset, many=True)

    
    astreintes = serializer.data

    for astreinte in astreintes:

        perm_id = astreinte["creneau"]["perm"]["id"]

        notation  = {
            "astreinte_type": astreinte["astreinte_type"],
            "note_deco": astreinte["note_deco"],
            "note_orga" : astreinte["note_orga"],
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
    for key in keys :
        if perms[key]["nb_note_deco"] > 0 :
            perms[key]["note_deco"] = round(perms[key]["note_deco"] / perms[key]["nb_note_deco"],2)
        if perms[key]["nb_note_menu"] > 0 :
            perms[key]["note_menu"] = round(perms[key]["note_menu"] / perms[key]["nb_note_menu"],2)
        if perms[key]["nb_note_orga"] > 0 :
            perms[key]["note_orga"] = round(perms[key]["note_orga"] / perms[key]["nb_note_orga"],2)
        if perms[key]["nb_note_anim"] > 0 :
            perms[key]["note_anim"] = round(perms[key]["note_anim"] / perms[key]["nb_note_anim"],2)

    return JsonResponse({'perms': list(perms.values())})


@api_view(['GET'])
@permission_classes((IsMemberUser,))
def get_perm_for_notation(request, perm_id):

    queryset = perm_models.Creneau.objects.filter(perm__id=perm_id)
    serializer = perm_serializers.CreneauSerializer(queryset, many=True)

    creneaux = serializer.data

    perm = dict()

    for creneau in creneaux : 

        if "creneau" not in perm : 

            perm = creneau["perm"]
            perm.pop("creneaux")
            perm["creneau"] = []
            perm["note_deco"] = 0
            perm["note_anim"] = 0
            perm["note_orga"] = 0
            perm["note_menu"] = 0
            perm["nb_note_deco"] = 0
            perm["nb_note_anim"] = 0
            perm["nb_note_orga"] = 0
            perm["nb_note_menu"] = 0
            perm["nb_astreintes"] = 0

        if not any(c for c in perm["creneau"] if c["id"] == creneau["id"]):

            creneau_data = creneau
            creneau_data.pop("perm")
            creneau_data.pop("state")
            creneau_data.pop("montantTTCMaxAutorise")
            creneau_data.pop('facturerecue_set')
            creneau_data["notation"] = []
            perm["creneau"].append(creneau_data)

    queryset = perm_models.Astreinte.objects.all()
    serializer = perm_serializers.AstreinteSerializer(queryset, many=True)

    
    astreintes = serializer.data

    for astreinte in astreintes:

        if perm_id == astreinte["creneau"]["perm"]["id"]:

            notation  = {
                "astreinte_type": astreinte["astreinte_type"],
                "note_deco": astreinte["note_deco"],
                "note_orga" : astreinte["note_orga"],
                "note_anim": astreinte["note_anim"],
                "note_menu": astreinte["note_menu"],
                "commentaire": astreinte["commentaire"]
            }

            if astreinte["note_deco"] > 0:
                perm["note_deco"] += astreinte["note_deco"]
                perm["nb_note_deco"] += 1
            if astreinte["note_anim"] > 0:
                perm["note_anim"] += astreinte["note_anim"]
                perm["nb_note_anim"] += 1
            if astreinte["note_orga"] > 0:
                perm["note_orga"] += astreinte["note_orga"]
                perm["nb_note_orga"] += 1
            if astreinte["note_menu"] > 0:
                perm["note_menu"] += astreinte["note_menu"]
                perm["nb_note_menu"] += 1
            perm["nb_astreintes"] += 1

            for creneau in perm["creneau"]:
                if creneau["id"] == astreinte["creneau"]["id"]:
                    creneau["notation"].append(notation)
                    break

    if perm["nb_note_deco"] > 0 :
        perm["note_deco"] = round(perm["note_deco"] / perm["nb_note_deco"],2)
    if perm["nb_note_menu"] > 0 :
        perm["note_menu"] = round(perm["note_menu"] / perm["nb_note_menu"],2)
    if perm["nb_note_orga"] > 0 :
        perm["note_orga"] = round(perm["note_orga"] / perm["nb_note_orga"],2)
    if perm["nb_note_anim"] > 0 :
        perm["note_anim"] = round(perm["note_anim"] / perm["nb_note_anim"],2)

    return JsonResponse(perm)


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser,))
def perm_may_be_requested(request):
    return JsonResponse({'perm_may_be_requested': config.__getattr__('PERM_MAY_BE_REQUESTED')})


@api_view(['POST'])
@permission_classes((IsAuthenticatedUser,))
def update_perm_may_be_requested_setting(request):
    if 'perm_may_be_requested' in request.data:
        perm_may_be_requested = request.data['perm_may_be_requested']
        config.__setattr__('PERM_MAY_BE_REQUESTED', perm_may_be_requested)
    return JsonResponse({})


class RequestedPermViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = perm_models.RequestedPerm.objects.filter(semestre_id=get_current_semester())
        serializer = perm_serializers.RequestedPermSerializer(queryset, many=True)

        return JsonResponse({'requested_perms': serializer.data})

    def create(self, request):
        if not self.perm_may_be_requested():
            return JsonResponse({'error': 'Il n\'est pas possible de demander une perm.'})
        serializer = perm_serializers.RequestedPermSerializer(request.data)
        requested_perm = serializer.data
        new_requested_perm = perm_models.RequestedPerm.objects.create(
            nom = requested_perm["nom"],
            asso = requested_perm["asso"],
            mail_asso = requested_perm["mail_asso"],
            nom_resp = requested_perm["nom_resp"],
            mail_resp = requested_perm["mail_resp"],
            nom_resp_2 = requested_perm["nom_resp_2"],
            mail_resp_2 = requested_perm["mail_resp_2"],
            theme = requested_perm["theme"],
            description = requested_perm["description"],
            membres = requested_perm["membres"],
            founder_login = requested_perm["founder_login"],
            ambiance = requested_perm["ambiance"],
            periode = requested_perm["periode"]
        )

        mail_content = "Coucou " + requested_perm["nom_resp"] + "\n\n" \
                        + "Ta demande de perm " +  requested_perm["nom"] + " a bien été enregistrée. Tu peux la modifier ici : \n\n" \
                        + "https://assos.utc.fr/perm/form?form_id=" + str(new_requested_perm.pk) + "\n\n" \
                        + "La bise, et à bientôt au Pic'Asso !"
        email = EmailMessage(
            subject=f"Pic'Asso - Demande de perm",
            body=mail_content,
            from_email=DEFAULT_FROM_EMAIL,
            to=[requested_perm["mail_resp"]],
        )
        email.send()

        return JsonResponse({"id": new_requested_perm.pk})

    def retrieve(self, request, pk=None):
        requested_perm = perm_models.RequestedPerm.objects.get(pk=pk)
        serializer = perm_serializers.RequestedPermSerializer(requested_perm)

        #Check if the user is the founder of the requested_perm object
        login = request.session.get('login')
        if login == serializer.data["founder_login"]:
            return JsonResponse({'perm': serializer.data})

        return JsonResponse({"error": "Vous n'avez pas la permission d'accéder à cette ressource"}, status=403)

    def update(self, request, pk=None):
        if not self.perm_may_be_requested():
            return JsonResponse({'error': 'Il n\'est pas possible de mettre à jour une perm.'})
        requested_perm = perm_models.RequestedPerm.objects.get(pk=pk)

        #Check if the user is the founder of the requested_perm object
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
            'nom', 'asso', 'mail_asso', 'nom_resp', 'mail_resp', 'nom_resp_2', 'mail_resp_2', 'theme', 'description', 'membres', 'founder_login',
            'ambiance', 'periode'    
        ])
        return JsonResponse({})

    def partial_update(self, request, pk=None):
        requested_perm = perm_models.RequestedPerm.objects.get(pk=pk)
        requested_perm.added = not requested_perm.added
        requested_perm.save()
        return JsonResponse({})

    def perm_may_be_requested(self):
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
    queryset = perm_models.RequestedPerm.objects.filter(semestre_id=get_current_semester())
    serializer = perm_serializers.RequestedPermSerializer(queryset, many=True)
    pdf = HtmlPdf()
    for requested_perm in serializer.data:
        requested_perm_content = render_to_string('requested_perm.html', {'requested_perm': requested_perm})
        pdf.add_page()
        pdf.write_html(requested_perm_content)
    response = HttpResponse(pdf.output(dest='S').encode('latin-1'))
    response['Content-Type'] = 'application/pdf'
    return response


@api_view(['GET'])
@permission_classes((IsAuthenticatedUser,))
def get_portal_assos(request):
    p = PortalClient()
    response = p.get_assos()
    return JsonResponse({'assos': response['data']}, status = response['status'])