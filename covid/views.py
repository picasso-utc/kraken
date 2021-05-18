from django.shortcuts import render
from django.http import JsonResponse
from covid import models as covid_models
from django.db.models import Sum
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET'])
def get_occupation(request):
    answer = {}
    queryPerson = covid_models.Person.objects.all().filter(depart__isnull=True).count()
    answer['person'] = queryPerson
    queryTableExt = covid_models.Person.objects.all().filter(depart__isnull=True,table__position="EXT").count()
    answer['tableExt'] = queryTableExt
    queryTableIn = covid_models.Person.objects.all().filter(depart__isnull=True,table__position="IN").count()
    answer['tableIn'] = queryTableIn
    queryCapacity = covid_models.Table.objects.aggregate(Sum('capacity'))
    answer['capacity'] = queryCapacity
#     queryCapacityExte = covid_models.Table.objects.filter(position="EXT").aggregate(Sum('capacity'))
    queryCapacityExte = covid_models.Table.objects.filter(position="EXT").count()
    answer['capacityExt'] = queryCapacityExte
#     queryCapacityIn = covid_models.Table.objects.filter(position="EXT").aggregate(Sum('capacity'))
    queryCapacityIn = covid_models.Table.objects.filter(position="IN").count()
    answer['capacityIn'] = queryCapacityIn
    return JsonResponse(answer)

