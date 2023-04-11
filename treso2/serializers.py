from rest_framework import serializers
from treso2.models import *

class SousCategorieFactureRecueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCategorieFactureRecue
        fields = ['id', 'nom', 'code']


class CategorieFactureRecueSerializer(serializers.ModelSerializer):
    sous_categories = SousCategorieFactureRecueSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = CategorieFactureRecue
        fields = ['id', 'nom', 'code', 'sous_categories']

    # Methode qui recupère un Json qui a les infos d'un catégorie et de ses sous-catégories et qui créer la catégorie
    # ainsi que les sous-catégories associés
    def create(self, validated_data):
        categorie = CategorieFactureRecue.objects.create(nom=validated_data['nom'], code=validated_data['code'])
        if('sous_categories' in validated_data):
            sous_categories_data = validated_data.pop('sous_categories')
            for sous_categorie_data in sous_categories_data:
                SousCategorieFactureRecue.objects.create(categorie=categorie, code=sous_categorie_data['code'], nom=sous_categorie_data['nom'])
        return categorie

    # Methode qui recupère un Json qui a les infos d'un catégorie et de ses sous-catégories et qui mets a jour la
    # catégorie ainsi que les sous-catégories associés
    def update(self, instance, validated_data):
        instance.nom = validated_data.get("nom", instance.nom)
        instance.code = validated_data.get("code", instance.code)
        codes_in_update=list()

        if ('sous_categories' in validated_data):
            sous_categories_data = validated_data.pop('sous_categories')
            for sous_categorie_data in sous_categories_data:
                codes_in_update.append(sous_categorie_data['code'])
                try:
                    obj = SousCategorieFactureRecue.objects.get(code=sous_categorie_data['code'], categorie=instance)
                    for key,value in sous_categorie_data.items():
                        setattr(obj,key,value)
                    obj.save()
                except SousCategorieFactureRecue.DoesNotExist:
                    SousCategorieFactureRecue.objects.create(categorie=instance, **sous_categorie_data)

            sous_categories = SousCategorieFactureRecue.objects.filter(categorie=instance)
            for sous_categorie in sous_categories:
                if (not sous_categorie.code in codes_in_update):
                    sous_categorie.delete()

        instance.save()
        return instance


class CategoriePrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePrix
        fields = ['prix', 'categorie']


class SousCategoriePrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCategoriePrix
        fields = ['prix', 'sous_categorie']


class ChequeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cheque
        fields = '__all__'


class FactureRecueSerializer(serializers.ModelSerializer):
    categorie_prix = CategoriePrixSerializer(many=True)
    sous_categorie_prix = SousCategoriePrixSerializer(many=True, required=False, allow_null=True)
    cheque = ChequeSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = FactureRecue
        fields = '__all__'

    def create(self, validated_data):
        if ('cheque' in validated_data):
            cheques_data = validated_data.pop('cheque')
        else:
            cheques_data = None
        if ('sous_categorie_prix' in validated_data):
            sous_categories_prix_data = validated_data.pop('sous_categorie_prix')
        else:
            sous_categories_prix_data = None
        categories_prix_data = validated_data.pop('categorie_prix')
        facture = FactureRecue.objects.create(**validated_data)
        if (cheques_data != None):
            for cheque_data in cheques_data:
                Cheque.objects.create(facture=facture, **cheque_data)
        for categorie_prix_data in categories_prix_data:
            CategoriePrix.objects.create(facture=facture, **categorie_prix_data)
        if(sous_categories_prix_data != None):
            for sous_categorie_prix_data in sous_categories_prix_data:
                SousCategoriePrix.objects.create(facture=facture, **sous_categorie_prix_data)
        facture.save()
        return facture

    def update(self, instance, validated_data):
        if ('cheque' in validated_data):
            cheques_data = validated_data.pop('cheque')
        else:
            cheques_data = None
        categories_prix_data = validated_data.pop('categorie_prix')
        if ('sous_categorie_prix' in validated_data):
            sous_categories_prix_data = validated_data.pop('sous_categorie_prix')
        else:
            sous_categories_prix_data = None
        for key,value in validated_data.items():
            setattr(instance,key,value)

        # Traite l'update de la base de donné associant un cheque et une facture
        if (cheques_data != None):
            cheque_in_update = list()
            for cheque_data in cheques_data:
                cheque_in_update.append(cheque_data['num'])
                try:
                    obj = Cheque.objects.get(facture=instance,num=cheque_data['num'])
                    for key, value in cheque_data.items():
                        setattr(obj,key,value)
                    obj.save()
                except Cheque.DoesNotExist:
                    Cheque.objects.create(facture=instance, **cheque_data)
            # Supprime les objets cheque qui etait associé a cette facture mais qui ne sont plus dans l'update
            cheques = Cheque.objects.filter(facture=instance)
            for cheque in cheques:
                if not cheque.num in cheque_in_update:
                    cheque.delete()

        # Traite l'update de la base de donné associant un prix a une categorie et une facture
        categories_in_update = list()
        for categorie_prix_data in categories_prix_data:
            categories_in_update.append(categorie_prix_data['categorie'])
            try:
                obj = CategoriePrix.objects.get(facture=instance,categorie=categorie_prix_data['categorie'])
                for key, value in categorie_prix_data.items():
                    setattr(obj,key,value)
                obj.save()
            except CategoriePrix.DoesNotExist:
                CategoriePrix.objects.create(facture=instance, **categorie_prix_data)
        # Supprime les objets CategoriePrix qui etait associé a cette facture mais qui ne sont plus dans l'update
        categories_prix = CategoriePrix.objects.filter(facture=instance)
        for categorie_prix in categories_prix:
            if not categorie_prix.categorie in categories_in_update:
                categorie_prix.delete()

        # Traite l'update de la base de donné associant un prix a une sous categorie et une facture
        if (sous_categories_prix_data != None):
            sous_categorie_in_update = list()
            for sous_categories_prix_data in sous_categories_prix_data:
                sous_categorie_in_update.append(sous_categories_prix_data['sous_categorie'])
                try:
                    obj = SousCategoriePrix.objects.get(facture=instance,sous_categorie=sous_categories_prix_data['sous_categorie'])
                    for key, value in sous_categories_prix_data.items():
                        setattr(obj,key,value)
                    obj.save()
                except SousCategoriePrix.DoesNotExist:
                    SousCategoriePrix.objects.create(facture=instance, **sous_categories_prix_data)
            # Supprime les objets SousCategoriePrix qui etait associé a cette facture mais qui ne sont plus dans l'update
            sous_categories_prix = SousCategoriePrix.objects.filter(facture=instance)
            for sous_categorie_prix in sous_categories_prix:
                if (not sous_categorie_prix.sous_categorie in sous_categorie_in_update):
                    sous_categorie_prix.delete()
        instance.save()
        return instance


class FactureEmiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactureEmise
        fields = '__all__'