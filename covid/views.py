from django.shortcuts import render
from covid import models as covid_models
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET'])
def get_occupation(request):
    answer = {}
    querySet = covid_models.Person.objects.all().filter(depart__isnull=True).count()
    answer['person'] = querySet
    return JsonResponse(answer)

