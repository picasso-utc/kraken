from rest_framework import viewsets
from tv import models as tv_models
from tv import serializers as tv_serializers
from survey import serializers as survey_serializers
from survey import models as survey_models
from perm import models as perm_models
from rest_framework.decorators import permission_classes, api_view
from django.http import JsonResponse, HttpResponse
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, IsMemberUserOrReadOnly
import qrcode


class WebTVViewSet(viewsets.ModelViewSet):
    """
    WebTV viewset
    """
    queryset = tv_models.WebTV.objects.all()
    serializer_class = tv_serializers.WebTVSerializer
    permission_classes = (IsMemberUserOrReadOnly,)


class WebTVLinkViewSet(viewsets.ModelViewSet):
    """
    WebTVLinks viewset
    """
    queryset = tv_models.WebTVLink.objects.all()
    serializer_class = tv_serializers.WebTVLinkSerializer
    permission_classes = (IsMemberUser,)


class WebTVMediaViewSet (viewsets.ModelViewSet):
    """
    TV Media viewset
    """
    queryset = tv_models.WebTVMedia.objects.all()
    serializer_class = tv_serializers.WebTVMediaSerializer
    permission_classes = (IsMemberUser,)


@api_view(['GET'])
def get_public_media(request):
    queryset = tv_models.WebTVMedia.objects.filter(activate=True)
    serializer = tv_serializers.WebTVMediaSerializer(queryset, many=True)
    return JsonResponse({'media' : serializer.data})


@api_view(['GET'])
def get_next_order_lines_for_tv(request):
    menu = perm_models.Menu.objects.last()
    if menu:
        orders = perm_models.OrderLine.objects.filter(menu_id=menu.id, quantity__gt=0, served=False, menu__is_closed=False, is_canceled=False).order_by('is_staff', 'id_transaction_payutc')
        buyers_list = list()
        for order in orders:
            buyers_list.append({'last_name': order.buyer_name, 'first_name': order.buyer_first_name, 'quantity': order.quantity})
        return JsonResponse({
            'menu': menu.article.nom,
            'orders': buyers_list
        })
    return JsonResponse({
        'menu' : '',
        'orders': []
    })



@api_view(['GET'])
def get_tv_public_surveys(request):
    queryset = survey_models.Survey.objects.filter(visible=True)
    serializer = survey_serializers.SurveySerializer(queryset, many=True)
    surveys = serializer.data
    for survey in surveys:
        total_vote = 0
        for item in survey['surveyitem_set']:
            total_vote += len(item["surveyitemvote_set"])
        for item in survey['surveyitem_set']:
            if total_vote == 0:
                item["vote"] = 0
            else :
                item["vote"] = len(item["surveyitemvote_set"])/total_vote
            del item["surveyitemvote_set"]
        survey['surveyitem_set'] = sorted(survey['surveyitem_set'], key= lambda item: item['vote'], reverse=True)
    return JsonResponse({'surveys' : surveys})

@api_view(['GET'])
def generate_qr_code(request):
    survey_id = request.GET.get("survey_id", None)
    url = 'https://assos.utc.fr/picasso'
    if survey_id:
        url += ('/poll/' + survey_id)
    img = qrcode.make(url)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response