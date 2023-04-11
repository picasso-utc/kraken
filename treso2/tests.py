from django.test import TestCase
from treso2.models import CategorieFactureRecue, SousCategorieFactureRecue, CategoriePrix, SousCategoriePrix, FactureRecue
from core.models import Semestre
from core.services.current_semester import get_current_semester
from treso2.serializers import CategorieFactureRecueSerializer, CategoriePrixSerializer, SousCategoriePrixSerializer,FactureRecueSerializer, FactureEmiseSerializer, ChequeSerializer
import datetime

# creating an instance of
# datetime.date
d1 = datetime.date(2023, 1, 1)
d2 = datetime.date(2023, 7, 1)
class CategorieTestCase(TestCase):
    def setUp(self):
        Semestre.objects.create(id=0, annee=2023, periode='P',start_date=d1, end_date=d2)
        CategorieFactureRecue.objects.create(nom="soft",code="S")
        CategorieFactureRecue.objects.create(nom="biere", code="B")
        SousCategorieFactureRecue.objects.create(nom="Pampryl",code="P",categorie=CategorieFactureRecue.objects.get(nom="soft"))
        SousCategorieFactureRecue.objects.create(nom="Pampry", code="B", categorie=CategorieFactureRecue.objects.get(nom="soft"))
        FactureRecue.objects.create(tva=5.5, prix=50, nom_entreprise="Intermarché", date=d1, personne_a_rembourser="Aymar",semestre=Semestre.objects.get(annee=2023))
        CategoriePrix.objects.create(categorie=CategorieFactureRecue.objects.get(nom="soft"), prix=30, facture=FactureRecue.objects.get(nom_entreprise="Intermarché"))
        SousCategoriePrix.objects.create(sous_categorie=SousCategorieFactureRecue.objects.get(nom='Pampryl'), prix=20, facture=FactureRecue.objects.get(nom_entreprise="Intermarché"))

    def test_categorie_creer(self):
        data={
            'id':CategorieFactureRecue.objects.get(nom='soft'),
            'nom':'Soft',
            'code':'C',
            'sous_categories':
                [{'nom':'Pampryl','code':'P'}]
        }
        serializer = CategorieFactureRecueSerializer(data=data)
        if (serializer.is_valid()):
            categorie = serializer.save()
            serialized_categorie = CategorieFactureRecueSerializer(instance=categorie)
            print(serialized_categorie.data)
        else:
            print(serializer.errors)


        """data={'tva':5.5,
              'prix':50,
              'nom_entreprise':'Intermarché',
              'date':d1,
              'semestre':get_current_semester(),
              'categorie_prix': [{'prix': 50, 'categorie': CategorieFactureRecue.objects.get(nom='soft').id},{'prix': 0, 'categorie': CategorieFactureRecue.objects.get(nom='biere').id}],
              'sous_categorie_prix': [{'prix': 50,'sous_categorie': SousCategorieFactureRecue.objects.get(nom='Pampryl').id}],
              'perm':None,
              'date_paiement':None,
              'date_remboursement':None,
              'moyen_paiement':None,
              'personne_a_rembourser':None,
              'remarque':None,
              'facture_number':None,
              'cheque':[{'num':0,
            'valeur':10,
            'state':'C',}]
              }
        serializer = FactureRecueSerializer(data=data)
        if(serializer.is_valid()):
            facture = serializer.save()
            serialized_facture = FactureRecueSerializer(instance=facture)
            print(serialized_facture.data)
        else:
            print(serializer.errors)"""
        """data={
            'tva': 5.5,
            'prix': 40,
            'destinataire': 'Geo Saglio',
            'nom_createur': "Pic'Asso",
            'date_due': datetime.date.today(),
            'etat':'D'
        }
        serializer = FactureEmiseSerializer(data=data)
        if (serializer.is_valid()):
            facture = serializer.save()
            serialized_facture = FactureEmiseSerializer(instance=facture)
            print(serialized_facture.data)
        else:
            print(serializer.errors)"""
        """data={
            'num':0,
            'valeur':10,
            'state':'C',
        }
        serializer = ChequeSerializer(data=data)
        if (serializer.is_valid()):
            cheque = serializer.save()
            serialized_facture = ChequeSerializer(instance=cheque)
            print(serialized_facture.data)
        else:
            print(serializer.errors)"""