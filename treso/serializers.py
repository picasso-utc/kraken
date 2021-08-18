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
        exclude = list()


class FactureRecuePermSerializer(serializers.ModelSerializer):
    class Meta:
        model = perm_models.Perm
        exclude_list = list()
        exclude = exclude_list


class FactureRecueCreneauSerializer(serializers.ModelSerializer):
    perm = FactureRecuePermSerializer(read_only=True)    
    class Meta:
        model = perm_models.Creneau
        exclude_list = list()
        exclude = exclude_list


class FactureRecueExtendedSerializer(serializers.ModelSerializer):
    perm = FactureRecueCreneauSerializer(read_only=True)
    cheque_set = ChequeListSerializer(required=False)
    personne_a_rembourser = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_paiement = serializers.DateField(required=False, allow_null=True)
    date_remboursement = serializers.DateField(required=False, allow_null=True)
    perm 
    class Meta:
        model = treso_models.FactureRecue
        exclude = list()

class FactureEmiseRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = treso_models.FactureEmiseRow
        exclude = list()


class FactureEmiseSerializer(serializers.ModelSerializer):
    factureemiserow_set = FactureEmiseRowSerializer(many = True, read_only = True)
    class Meta:
        model = treso_models.FactureEmise
        exclude = list()


class FactureEmiseWithRowsSerializer(serializers.ModelSerializer):
    factureemiserow_set = FactureEmiseRowSerializer(many = True, read_only = True)
    # factureemiserow_set = FactureEmiseRowListSerializer()
    class Meta:
        model = treso_models.FactureEmise
        exclude = list()


class ReversementEffectueSerializer(serializers.ModelSerializer):
    class Meta:
        model = treso_models.ReversementEffectue
        exclude = list()


class SimpleFactureRecueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = treso_models.FactureRecue
        fields = ('id', )

SimpleFactureRecueListSerializer = SimpleFactureRecueSerializer.many_init

