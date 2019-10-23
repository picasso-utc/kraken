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

class PosteSerializer(serializers.ModelSerializer):
	# Serializer des postes existants
    class Meta:
        model = core_models.Poste
        fields = ('nom', 'order')

class MemberSerializer(serializers.ModelSerializer):
    # Serializer des membres existants
    class Meta:
        model = core_models.Member
        fields = ('id', 'userright_id', 'semester_id', 'poste_id', 'picture')