from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from core.services.current_semester import get_current_semester


# class User(AbstractBaseUser):
class UserRight(models.Model):
    """
    Modèle de gestion des droits utilisateurs.
    On distingue plusieurs types de droits, à travers la valeur de 'right'.
    Par défaut, un utilisateur qui n'a aucun UserRight revient à un utilisateur
    qui a un utilisateur qui a comme right 'USERRIGHT_NONE'
    """
    USERRIGHT_ALL = 'A'
    USERRIGHT_MEMBER = 'M'
    USERRIGHT_NONE = 'N'

    USERRIGHT_CHOICES = (
        (USERRIGHT_ALL, 'Accès total'),
        (USERRIGHT_MEMBER, 'Accès membre'),
        (USERRIGHT_NONE, 'Accès interdit'),
    )

    login = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=50, null=True)
    right = models.CharField(max_length=1, choices=USERRIGHT_CHOICES)
    last_login = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Semestre(models.Model):
    """Modèle représentant un semestre de cours."""
    SEMESTRE_AUTOMNE = 'A'
    SEMESTRE_PRINTEMPS = 'P'

    SEMESTRE_CHOICES = (
        (SEMESTRE_AUTOMNE, 'Automne'),
        (SEMESTRE_PRINTEMPS, 'Printemps'),
    )

    annee = models.IntegerField()
    periode = models.CharField(max_length=1, choices=SEMESTRE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    solde_debut = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.periode}{self.annee}"

    def get_paid_bills(self):
        from treso.models import FactureEmise, FactureRecue
        sum_paid_received_bills = sum(fac.prix
                                      for fac in FactureRecue.objects.filter(semestre=self,
                                                                             etat=FactureRecue.FACTURE_PAYEE))
        sum_paid_outvoiced_bills = sum(fac.get_total_ttc_price()
                                       for fac in FactureEmise.objects.filter(semestre=self,
                                                                              etat=FactureEmise.FACTURE_PAYEE))
        return {
            'sum_paid_received_bills': sum_paid_received_bills,
            'sum_paid_outvoiced_bills': sum_paid_outvoiced_bills,
        }


class PricedModel(models.Model):
    """
    Classe abstraite qui représente tout objet qui a un prix.
    """
    tva = models.FloatField(default=0)  # TVA en decimal, type 5.5, 20...
    prix = models.FloatField(default=0)  # prix TTC

    def get_price_without_taxes(self):
        """ À partir du prix TTC sauvegardé de l'objet, obtenir le prix HT """
        return round(self.prix * (100 / (100 + self.tva)), 2)

    def get_total_taxes(self):
        """ À partir du prix TTC sauvegardé de l'objet, obtenir la TVA """
        return round(self.prix - self.get_price_without_taxes(), 2)

    class Meta:
        """ Représentation en DB """
        abstract = True


class PeriodeTVA(models.Model):
    """
    Class abstraire, Période de TVA.
    """
    PERIODE_NON_DECLAREE = 'N'
    PERIODE_DECLAREE = 'D'

    PERIODE_CHOICES = (
        (PERIODE_NON_DECLAREE, 'Non déclarée'),
        (PERIODE_DECLAREE, 'Déclarée'),
    )

    state = models.CharField(max_length=1, choices=PERIODE_CHOICES, default='N')
    debut = models.DateField()
    fin = models.DateField()

    class Meta:
        """ Représentation en DB """
        abstract = False


class Poste(models.Model):
    """
    Classe qui regroupe tous les postes du Pic
    """
    order = models.IntegerField()
    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return f"{self.name}"


class Member(models.Model):
    """
    Classe qui regroupe tous les membres du pic
    """
    userright = models.ForeignKey(UserRight, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, default=get_current_semester)
    poste = models.ForeignKey(Poste, null=True, on_delete=models.SET_NULL)
    picture = models.ImageField(upload_to="member", null=True, blank=True, default=None)


class BlockedUser(models.Model):
    """
    Classe qui regroupe tous les utilisateurs bloqués
    """
    cas = models.CharField(null=False, default=None, max_length=8, blank=False, unique=True)
    name = models.CharField(null=False, default=None, max_length=255, blank=False)
    justification = models.CharField(null=False, default=None, max_length=255, blank=False)
    date = models.DateField(auto_now_add=True, blank=True)


class PersonPerHour(models.Model):
    """
    Classe qui regroupe toutes les lectures de badges à l'entree du pic #COVID
    """
    first_name = models.CharField(null=False, default=None, max_length=255, blank=False)
    last_name = models.CharField(null=False, default=None, max_length=255, blank=False)
    user_id = models.CharField(null=False, default=None, max_length=10, blank=False, unique=False)
    date_time = models.DateTimeField(auto_now_add=True, blank=True)
