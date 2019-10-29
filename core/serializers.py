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
        fields = ('id', 'login', 'right', 'last_login', 'name')

class PosteSerializer(serializers.ModelSerializer):
	# Serializer des postes existants
    class Meta:
        model = core_models.Poste
        exclude = list()

class MemberSerializer(serializers.ModelSerializer):
    userright = UserRightSerializer(read_only=True)
    userright_id = serializers.PrimaryKeyRelatedField(queryset=core_models.UserRight.objects.all(), source="userright")
    
    # Serializer des membres existants
    class Meta:
        model = core_models.Member
        exclude = list()

class ShortMemberSerializer(serializers.ModelSerializer):

    userright = UserRightSerializer(read_only=True)

    # Serializer des membres existants
    class Meta:
        model = core_models.Member
        fields = ('userright',)