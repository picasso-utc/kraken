from rest_framework import serializers

from core import models as core_models

class SemestreSerializer(serializers.ModelSerializer):
	# Serializer des semestres
    class Meta:
        model = core_models.Semestre
        fields = ('id', 'annee', 'periode', 'start_date', 'end_date')


class PeriodeTVASerializer(serializers.ModelSerializer):
	# Serializer de la periode de TVA
	class Meta:
		model = core_models.PeriodeTVA
		fields = ('id', 'state', 'debut', 'fin')


class UserRightSerializer(serializers.ModelSerializer):
	# Serializer des droits des utilisateurs
    class Meta:
        model = core_models.UserRight
        fields = ('id', 'login', 'right', 'last_login')