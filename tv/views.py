from rest_framework import viewsets
from tv import models as tv_models
from tv import serializers as tv_serializers
from rest_framework.decorators import permission_classes, api_view
from django.http import JsonResponse
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
