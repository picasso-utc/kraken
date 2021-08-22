from rest_framework import serializers
from chopin import models as chopin_models

class NewsLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = chopin_models.Newsletter
        exclude = list()
