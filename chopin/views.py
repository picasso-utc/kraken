from django.shortcuts import render
from rest_framework.decorators import api_view


@api_view(['GET'])
def get_calendar(request):
    return JsonResponse(calendar)

@api_view(['GET'])
def get_newsletters(request):
    return JsonResponse(newsletters)
