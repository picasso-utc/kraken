# -*- coding: utf-8 -*-

from rest_framework import viewsets
from rest_framework.response import Response


class RetrieveSingleInstanceModelViewSet(viewsets.ModelViewSet):
    """
    Lorsqu'on utilise ce Viewset, qui hérite de ModelViewSet, on définit, en plus de
    serializer_class, un objet single_serializer_class, qui sera utilisé en sortie lorsqu'il
    n'y a qu'un seul objet récupéré.
    C'est utile lorsqu'on veut ressortir certains champs seulement à la récupération d'un
    objet particulier, et pas quand on récupère tous les objets.
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.single_serializer_class(instance)
        return Response(serializer.data)
