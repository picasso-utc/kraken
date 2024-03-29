from rest_framework import serializers
from perm import models as perm_models
from treso import serializers as treso_serializers
from core import serializers as core_serializers
from core import models as core_models


class RequestedPermSerializer(serializers.ModelSerializer):
    class Meta:
        model = perm_models.RequestedPerm
        exclude = list()


class PermSerializer(serializers.ModelSerializer):
    creneaux = serializers.StringRelatedField(many=True, required=False, read_only=True)

    class Meta:
        model = perm_models.Perm
        exclude_list = list()
        exclude = exclude_list


class PermPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = perm_models.Perm
        fields = ('nom',)


class ArticleSerializer(serializers.ModelSerializer):
    creneau = serializers.PrimaryKeyRelatedField(queryset=perm_models.Creneau.objects.all())
    menu = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = perm_models.Article
        exclude = list()


class CreneauSerializer(serializers.ModelSerializer):
    perm = PermSerializer(read_only=True)
    facturerecue_set = treso_serializers.FactureRecueSerializer(many=True, read_only=True)
    article_set = ArticleSerializer(many=True, read_only=True)
    perm_id = serializers.PrimaryKeyRelatedField(queryset=perm_models.Perm.objects.all(), source="perm")

    class Meta:
        model = perm_models.Creneau
        exclude_list = list()
        exclude = exclude_list


class CreneauAstreinteSerializer(serializers.ModelSerializer):
    perm = PermPublicSerializer(read_only=True)
    astreintes = serializers.StringRelatedField(many=True, required=False, read_only=True)
    size = serializers.SerializerMethodField()

    def get_size(self, instance):
        return instance.get_size()
    
    class Meta:
        model = perm_models.Creneau
        fields = ('id', 'perm', 'creneau', 'date', 'astreintes', 'size')


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


class AstreinteSerializer(serializers.ModelSerializer):
    creneau = CreneauSerializer(read_only=True)
    creneau_id = serializers.PrimaryKeyRelatedField(queryset=perm_models.Creneau.objects.all(), source="creneau")
    member = core_serializers.ShortMemberSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(queryset=core_models.Member.objects.all(), source="member")

    class Meta:
        model = perm_models.Astreinte
        exclude = list()

class ShotgunSerializer(serializers.ModelSerializer):
    launched_by = core_serializers.ShortMemberSerializer(read_only=True)
    launched_by_id = serializers.PrimaryKeyRelatedField(queryset=core_models.Member.objects.all(), source="launched_by")

    class Meta:
        model = perm_models.Shotgun
        exclude = list()


class PermHalloweenSerializer(serializers.ModelSerializer):
    class Meta:
        model = perm_models.PermHalloween
        fields = ('id', 'login', 'article_id')
