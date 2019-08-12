from rest_framework import serializers

from treso import models as treso_models
from perm import models as perm_models


class CategorieFactureRecueSerializer(serializers.ModelSerializer):
    class Meta:
        model = treso_models.CategorieFactureRecue
        fields = ('id', 'nom', 'code')


class ChequeSerializer(serializers.ModelSerializer):
    class Meta:
        model = treso_models.Cheque
        exclude = list()
ChequeListSerializer = ChequeSerializer.many_init


class FactureRecueSerializer(serializers.ModelSerializer):
    cheque_set = ChequeListSerializer(required=False)
    personne_a_rembourser = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_paiement = serializers.DateField(required=False, allow_null=True)
    date_remboursement = serializers.DateField(required=False, allow_null=True)
    class Meta:
        model = treso_models.FactureRecue
        exclude = ('semestre', )


class FactureEmiseRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = treso_models.FactureEmiseRow
        exclude = list()


class FactureEmiseSerializer(serializers.ModelSerializer):
    factureemiserow_set = FactureEmiseRowSerializer(many = True, read_only = True)
    class Meta:
        model = treso_models.FactureEmise
        exclude = ('semestre', )

# FactureEmiseRowListSerializer = FactureEmiseRowSerializer.many_init


class FactureEmiseWithRowsSerializer(serializers.ModelSerializer):
    factureemiserow_set = FactureEmiseRowSerializer(many = True, read_only = True)
    # factureemiserow_set = FactureEmiseRowListSerializer()
    class Meta:
        model = treso_models.FactureEmise
        exclude = ('semestre',)


class ReversementEffectueSerializer(serializers.ModelSerializer):
    class Meta:
        model = treso_models.ReversementEffectue
        exclude = list()


# class SimplePermSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = perm_models.Perm
#         fields = ('id', 'nom')








class SimpleFactureRecueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = treso_models.FactureRecue
        fields = ('id', )

SimpleFactureRecueListSerializer = SimpleFactureRecueSerializer.many_init





# FactureRecueListSerializer = FactureRecueSerializer.many_init














# class TvaInfo(serializers.Serializer):
#     pass
