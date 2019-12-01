from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
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