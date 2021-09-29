from rest_framework import serializers
from shotgun import models as shotgun_model


class CreneauSerializer(serializers.ModelSerializer):
    class Meta:
        model = shotgun_model.Creneau
        exclude = list()

class UserInShotgunSerializer(serializers.ModelSerializer):
    class Meta:
        model = shotgun_model.UserInShotgun
        exclude = list()