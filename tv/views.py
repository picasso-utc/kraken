from rest_framework import viewsets
from tv import models as tv_models
from tv import serializers as tv_serializers
from rest_framework.decorators import permission_classes
from core.permissions import IsAdminUser, IsAuthenticatedUser, IsMemberUser


class WebTVViewSet(viewsets.ModelViewSet):
    """
    WebTV viewset
    """
    queryset = tv_models.WebTV.objects.all()
    serializer_class = tv_serializers.WebTVSerializer
    permission_classes = (IsAdminUser,)


class WebTVLinkViewSet(viewsets.ModelViewSet):
    """
    WebTVLinks viewset
    """
    queryset = tv_models.WebTVLink.objects.all()
    serializer_class = tv_serializers.WebTVLinkSerializer
    permission_classes = (IsAdminUser,)

    # def get_queryset(self):
    #     queryset = tv_models.TVConfiguration.objects.all()
    #     if self.request.query_params.get('tv'):
    #         query = self.request.query_params.get('tv')
    #         queryset = queryset.filter(tv__id=query).order_by('-id')[:1]
    #     return queryset

    # def post(self):
    #     print(self.request.data)

class WebTVMediaViewSet (viewsets.ModelViewSet):
    """
    TV Media viewset
    """
    queryset = tv_models.WebTVMedia.objects.all()
    serializer_class = tv_serializers.WebTVMediaSerializer
    permission_classes = (IsMemberUser,)
