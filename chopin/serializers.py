from rest_framework import serializers
from chopin import models as chopin_models

class NewsLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = chopin_models.Newsletter
        exclude = list()

class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = chopin_models.Calendar
        exclude = list()

class PermToCalendar(serializers.ModelSerializer):
    responsable = serializers.CharField(source='perm.nom_resp')
    semestre = serializers.IntegerField(source='perm.semestre_id')
    description = serializers.IntegerField(source='perm.asso')
    nom = serializers.CharField(source='perm.nom')
    periode = serializers.CharField(source='creneau')
    class Meta:
        model = chopin_models.Calendar
        fields=['responsable','semestre','nom','description', 'date', 'hour','periode']
