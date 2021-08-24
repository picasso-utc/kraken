from datetime import date, timedelta

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets
from chopin import models as chopin_models
from core.services.current_semester import get_current_semester
from perm import models as perms_models
from chopin import serializers as chopin_serializers
from chopin.serializers import NewsLetterSerializer, PermToCalendar, CalendarSerializer
from core.models import UserRight
from core.permissions import FULL_CONNEXION, IsAdminUser


class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.Newsletter.objects.all()
    serializer_class = chopin_serializers.NewsLetterSerializer

    def create(self, request, *args, **kwargs):
        """
        verify that the author of the post request have the right to create a newsletter
        """
        right = request.session.get('right')
        login = request.session.get('login')
        has_full_connexion = request.session.get('connexion') == FULL_CONNEXION
        if right == 'A' and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion:
            id = self.request.query_params.get('id')
            if id is None:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=201, headers=headers)
            else:
                queryset = chopin_models.Newsletter.objects.filter(id=id)
                serializer = NewsLetterSerializer(queryset, many=True)
                if len(serializer.data) == 0:
                    return JsonResponse({})
                else:
                    print(request.data)
                    queryset.update(title=request.data['title'], content=request.data['content'],
                                    publication_date=request.data['publication_date'])
                    return JsonResponse({})
        else:
            return Response(status=403)

    def list(self, request, pk=None):
        id = self.request.query_params.get('id')
        if id is None:
            queryset = chopin_models.Newsletter.objects.all()
            serializer = NewsLetterSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = chopin_models.Newsletter.objects.filter(id=id)
            serializer = NewsLetterSerializer(queryset, many=True)
            return Response(serializer.data)

    def put(self, request, ):
        print('edit the newsletter')

    def delete(self, request, ):
        id = self.request.query_params.get('id')
        if id is None:
            return JsonResponse({})
        else:
            chopin_models.Newsletter.objects.filter(id=id).delete()
            return JsonResponse({})


class CalendarViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.Calendar.objects.all()
    serializer_class = chopin_serializers.CalendarSerializer
    def list(self, request, *args, **kwargs):
        try:
            nb = int(self.request.query_params.get('nb'))
        except TypeError:
            nb = 7
        startdate = date.today()
        enddate = startdate + timedelta(days=nb)
        queryset = perms_models.Creneau.objects.select_related('perm').filter(perm__semestre=get_current_semester()).filter(date__range=[startdate, enddate])
        serializer = PermToCalendar(queryset, many=True)
        queryset = chopin_models.Calendar.objects.all().filter(semestre=get_current_semester()).filter(date__range=[startdate, enddate])
        value = serializer.data
        serializer = CalendarSerializer(queryset, many=True)
        value += serializer.data
        return Response(value)


    def delete(self, request, ):
        id = self.request.query_params.get('id')
        if id is None:
            return JsonResponse({})
        else:
            chopin_models.Calendar.objects.filter(id=id).delete()
            return JsonResponse({})

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        elif self.request.method == "POST":
            return [IsAdminUser()]
        elif self.request.method == "DELETE":
            return [IsAdminUser()]
        else:
            return []

