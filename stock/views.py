"""
WIP

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView

from core.permissions import IsAdminUser
from stock.helper import update_supply_csv, update_sharepoint
from stock.models import Supply
from stock.serializers import StockSerializer


class SupplyViewSet(ListCreateAPIView):
    queryset = Supply.objects.all()
    serializer_class = StockSerializer
    permission_classes = (IsAdminUser,)


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def trigger_end_supply(request):
    update_supply_csv()
    update_sharepoint('stock/supply.csv', 'supply.csv')
    return HttpResponse(status=200)
"""

