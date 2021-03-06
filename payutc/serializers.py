from rest_framework import serializers

from payutc.models import GoodiesWinner

class GoodiesWinnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodiesWinner
        fields = ('id', 'winner', 'picked_up')

