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
        fields = ['responsable', 'semestre', 'nom', 'description', 'date', 'hour', 'periode']


class TypeDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = chopin_models.PlanningTypeJour
        exclude = list()


class CreneauSerializer(serializers.ModelSerializer):
    class Meta:
        model = chopin_models.PlanningCreneau
        exclude = list()


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = chopin_models.PlanningJob
        exclude = list()


class ListJobDay(serializers.ModelSerializer):
    id = serializers.CharField(source='id_job__id')
    titre = serializers.CharField(source='id_job__titre')
    description = serializers.CharField(source='id_job__description')
    nb = serializers.IntegerField()
    hour = serializers.CharField(source='id_creneau__hour')
    duree = serializers.CharField(source='id_creneau__duree')

    class Meta:
        model = chopin_models.PlanningJob
        exclude = list()
        fields = ('id', 'titre', 'description', 'nb', 'hour', 'duree')


class CotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = chopin_models.PlanningCota
        exclude = list()
