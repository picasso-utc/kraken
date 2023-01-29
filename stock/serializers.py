"""
WIP

from rest_framework import serializers

from core.models import Semestre
from stock.models import Supply


class StockSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        current_semester = Semestre.objects.latest('id')

        validated_data['semester_id'] = current_semester.id
        return Supply.objects.create(**validated_data)

    class Meta:
        model = Supply
        exclude = list()
"""
