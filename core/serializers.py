from rest_framework import serializers

from core.models import Semestre, UserRight

class SemestreSerializer(serializers.ModelSerializer):
	# Serializer des semestres
    class Meta:
        model = Semestre
        fields = ('id', 'annee', 'periode', 'start_date', 'end_date')


class UserRightSerializer(serializers.ModelSerializer):
	# Serializer des droits des utilisateurs
    class Meta:
        model = UserRight
        fields = ('id', 'login', 'right', 'last_login')