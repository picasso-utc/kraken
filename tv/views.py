from rest_framework import viewsets
from tv import models as tv_models
from tv import serializers as tv_serializers
from perm import models as perm_models
from rest_framework.decorators import permission_classes, api_view
from django.http import JsonResponse
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser, IsMemberUserOrReadOnly


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
