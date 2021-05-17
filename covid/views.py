from django.shortcuts import render
from django.http import JsonResponse
from covid import models as covid_models
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET'])
def get_occupation(request):
    answer = {}
    queryPerson = covid_models.Person.objects.all().filter(depart__isnull=True).count()
    answer['person'] = querySet
    queryTableExt = covid_models.Table.objects.all().filter(person__depart__isnull=True,position="EXT").count()
    answer['tableExt'] = querySet
    queryTableIn = covid_models.Table.objects.all().filter(person__depart__isnull=True,position="IN").count()
    answer['tableIn'] = querySet
    return JsonResponse(answer)

