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
        exclude = exclude_list

class PermPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = perm_models.Perm
        fields = ('nom',)


class ArticleSerializer(serializers.ModelSerializer):
    creneau = serializers.PrimaryKeyRelatedField(queryset = perm_models.Creneau.objects.all())
    menu = serializers.StringRelatedField(many=True, read_only=True)

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


class CreneauPublicSerializer(serializers.ModelSerializer):
    
    perm = PermPublicSerializer(read_only=True)    

    class Meta:
        model = perm_models.Creneau
        fields = ('id', 'perm', 'creneau', 'date')
    

class OrderLinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = perm_models.OrderLine


class MenuSerializer(serializers.ModelSerializer):
    article = ArticleSerializer()

    class Meta:
        model = perm_models.Menu
        fields = ('article',)

        
class SignatureSerializer(serializers.ModelSerializer):
    creneau = CreneauSerializer(read_only=True) 
    creneau_id = serializers.PrimaryKeyRelatedField(queryset=perm_models.Creneau.objects.all(), source="creneau")
    class Meta:
        model = perm_models.Signature
        exclude_list = list()
        exclude = exclude_list
