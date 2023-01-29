from datetime import date, timedelta
from typing import OrderedDict
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import viewsets
from chopin import models as chopin_models
from core.services.current_semester import get_current_semester
from perm import models as perms_models
from chopin import serializers as chopin_serializers
from chopin.serializers import BeerInfoSerializer, NewsLetterSerializer, PermToCalendar, CalendarSerializer, TrendingProductSerializer
from core.models import UserRight
from core.permissions import FULL_CONNEXION, IsAdminUser, IsMemberUser


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
        if right == 'A' or right == 'M' and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion:
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
            start_days = int(self.request.query_params.get('startDays'))
            end_days = int(self.request.query_params.get('endDays'))

        except TypeError:
            start_days = 0
            end_days = 7

        today = date.today()
        start_date = today + timedelta(days=start_days)
        end_date = today + timedelta(days=end_days)

        queryset = perms_models.Creneau.objects.select_related('perm').filter(
            perm__semestre=get_current_semester()).filter(date__range=[start_date, end_date])
        perm_serializer = PermToCalendar(queryset, many=True)
        value = perm_serializer.data

        periode_sorted_perm_list= sorted(value, key=lambda X: 3 if X['periode']=="S" else 2 if X['periode']=='D' else 1)
        sorted_perm_list = sorted(periode_sorted_perm_list, key=lambda X:X['date'])
        sorted_perm_calendar={}

        for perm in sorted_perm_list:
            if perm['date'] in sorted_perm_calendar.keys():
                sorted_perm_calendar[perm['date']].append(perm)
            else:
                sorted_perm_calendar[perm['date']]=[perm]

        return JsonResponse(sorted_perm_calendar)

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
            return [IsMemberUser()]
        elif self.request.method == "DELETE":
            return [IsMemberUser()]
        else:
            return []


class TrendingProductViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.TrendingProduct.objects.all()
    serializer_class = chopin_serializers.TrendingProductSerializer

    def create(self, request, *args, **kwargs):
        right = request.session.get('right')
        login = request.session.get('login')
        has_full_connexion = request.session.get('connexion') == FULL_CONNEXION
        if right == 'A' or right == 'M' and (UserRight.objects.filter(login=login, right=right).count()) and has_full_connexion:
            if chopin_models.TrendingProduct.objects.count() > 0:
                chopin_models.TrendingProduct.objects.all().delete()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response(status=403)


class EvenementsViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.Evenements.objects.all()
    serializer_class = chopin_serializers.EvenementSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        elif self.request.method == "POST":
            return [IsMemberUser()]
        elif self.request.method == "DELETE":
            return [IsMemberUser()]
        else:
            return []

class BeerInfoViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.BeerInfo.objects.all()
    serializer_class = chopin_serializers.BeerInfoSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        elif self.request.method == "POST":
            return [IsMemberUser()]
        elif self.request.method == "DELETE":
            return [IsMemberUser()]
        else:
            return []

class TypeDayViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.PlanningTypeJour.objects.all()
    serializer_class = chopin_serializers.TypeDaySerializer


class CreneauViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.PlanningCreneau.objects.all()
    serializer_class = chopin_serializers.CreneauSerializer


class JobViewSet(viewsets.ModelViewSet):
    queryset = chopin_models.PlanningJob.objects.all()
    serializer_class = chopin_serializers.JobSerializer

    def list(self, request, *args, **kwargs):
        try:
            nb = int(self.request.query_params.get('id_day'))
        except TypeError:
            nb = 0
        if nb != 0:
            queryset = chopin_models.PlanningCota.objects.filter(id_typejour=nb).values('id_job__titre', 'id_job__id',
                                                                                        'id_job__description', 'nb',
                                                                                        'id_creneau__hour',
                                                                                        'id_creneau__duree').distinct()
            serializer = chopin_serializers.ListJobDay(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = chopin_models.PlanningJob.objects.all()
            serializer = chopin_serializers.JobSerializer(queryset, many=True)
            return Response(serializer.data)


class CotaViwSet(viewsets.ModelViewSet):
    queryset = chopin_models.PlanningCota.objects.all()
    serializer_class = chopin_serializers.CotaSerializer
