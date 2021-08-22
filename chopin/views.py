from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
from chopin import models as chopin_models
from chopin import serializers as chopin_serializers
from chopin.serializers import NewsLetterSerializer
from core.models import UserRight
from core.permissions import FULL_CONNEXION


class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.Newsletter.objects.all()
    serializer_class = chopin_serializers.NewsLetterSerializer
    def create(self, request, *args, **kwargs):
        """
        verify that the author of the post request have the right to create a newsletter
        """
        print(request.data)
        right = request.session.get('right')
        login = request.session.get('login')
        has_full_connexion = request.session.get('connexion') == FULL_CONNEXION
        if right == 'A' and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response(status=403)

    def retrieve(self, request, pk=None):
        pass
        print('Get')
        queryset = chopin_models.Newsletter.objects.all()
        news = get_object_or_404(queryset, pk=pk)
        serializer = NewsLetterSerializer(news)
        return Response(serializer.data)

    def list(self, request, pk=None):
        id = self.request.query_params.get('id')
        print(id)
        if id is None:
            queryset = chopin_models.Newsletter.objects.all()
            serializer = NewsLetterSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = chopin_models.Newsletter.objects.filter(id=id)
            serializer = NewsLetterSerializer(queryset, many=True)
            return Response(serializer.data)

    def put(self, request,):
        print('edit the newsletter')

    def delete(self, request,):
        id = self.request.query_params.get('id')
        if id is None:
            return JsonResponse({})
        else:
            chopin_models.Newsletter.objects.filter(id=id).delete()
            return JsonResponse({})
