from rest_framework import serializers
from perm import models as perm_models
from treso import serializers as treso_serializers
from core import serializers as core_serializers
from core import models as core_models


class PermSerializer(serializers.ModelSerializer):
    creneaux = serializers.StringRelatedField(many=True, required=False, read_only=True)
    semestre = serializers.StringRelatedField(many=False, read_only=True)
    # semestre_id = serializers.PrimaryKeyRelatedField(queryset=core_models.Semestre.objects.all(), source="semestre")

    class Meta:
        model = perm_models.Perm
        exclude_list = list()
        # if not is_admin() :
            # exclude_list = ('id', 'nom_resp', 'mail_resp', 'semestre_id')
        exclude = exclude_list


class ArticleSerializer(serializers.ModelSerializer):
    creneau = serializers.PrimaryKeyRelatedField(queryset = perm_models.Creneau.objects.all())

    class Meta:
        model = perm_models.Article
        exclude = list()


class CreneauSerializer(serializers.ModelSerializer):
    
    perm = PermSerializer(read_only=True)    
    facturerecue_set = treso_serializers.FactureRecueSerializer(many = True, read_only = True)
    article_set = ArticleSerializer(many=True, read_only=True)
    perm_id = serializers.PrimaryKeyRelatedField(queryset=perm_models.Perm.objects.all(), source="perm")

    class Meta:
        model = perm_models.Creneau
        exclude_list = list()
        # if not is_admin():
            # exclude_list = ('state', 'montantTTCMaxAutorise', 'id', 'perm_id')
        exclude = exclude_list
    

class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = perm_models.Signature
        fields = ('id', 'nom', 'perm', 'date', 'login')
