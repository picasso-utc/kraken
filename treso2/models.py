import datetime

from django.db import models
from perm.models import Creneau
from core.models import Semestre
from core.services.current_semester import get_current_semester
from django.dispatch import receiver


# Models pour les nouveau piscous

class CategorieFactureRecue(models.Model):
    nom = models.CharField(max_length=255)
    code = models.CharField(max_length=1, unique=True)

    # Fonction pour afficher que le code dans les serializer qui appellent les catégories
    def __str__(self):
        return '%s' % (self.code)

class SousCategorieFactureRecue(models.Model):
    categorie = models.ForeignKey(CategorieFactureRecue, on_delete=models.CASCADE, related_name="sous_categories")
    code = models.CharField(max_length=1)
    nom = models.CharField(max_length=255)

    class Meta:
        db_table = 'treso2_souscategoriefacturerecue'
        constraints = [
            models.UniqueConstraint(fields=['categorie','code'],name='unique Code for sous categorie')
        ]

    #Fonction pour afficher que le code dans les serializer qui appellent les sous catégories
    #utiliser pour les sous catégorie prix et permet aussi de savoir a quelle categorie appartient cette sous categorie
    def __str__(self):
        return '%d / %s' % (self.categorie.id , self.code)

class FactureRecue(models.Model):
    FACTURE_A_PAYER = 'D'
    FACTURE_A_REMBOURSER = 'R'
    FACTURE_EN_ATTENTE = 'E'
    FACTURE_PAYEE = 'P'

    FACTURE_STATES = (
        (FACTURE_A_PAYER, 'À payer'),
        (FACTURE_A_REMBOURSER, 'À rembourser'),
        (FACTURE_EN_ATTENTE, 'En attente'),
        (FACTURE_PAYEE, 'Payée'),
    )

    tva = models.FloatField(default=0)  # TVA en decimal, type 5.5, 20...
    prix = models.FloatField(default=0)  # prix TTC
    perm = models.ForeignKey(Creneau, on_delete=models.CASCADE, null=True, default=None, related_name="request_for_picsous")
    etat = models.CharField(max_length=1, choices=FACTURE_STATES, default=FACTURE_A_PAYER)
    nom_entreprise = models.CharField(max_length=255)
    date = models.DateField()
    date_created = models.DateTimeField(null=True, default=datetime.datetime.now())
    date_paiement = models.DateField(null=True, default=None)
    date_remboursement = models.DateField(null=True, default=None)
    moyen_paiement = models.CharField(null=True, default=None, max_length=255)
    personne_a_rembourser = models.CharField(null=True, default=None, max_length=255)
    immobilisation = models.BooleanField(default=False)
    remarque = models.TextField(null=True, default=None)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, null=True, default=get_current_semester, related_name="request_for_picsous")
    facture_number = models.TextField(null=True, blank=True, default=None)

    def get_price_without_taxes(self):
        """ À partir du prix TTC sauvegardé de l'objet, obtenir le prix HT """
        return round(self.prix * (100 / (100 + self.tva)), 2)

    def get_total_taxes(self):
        """ À partir du prix TTC sauvegardé de l'objet, obtenir la TVA """
        return round(self.prix - self.get_price_without_taxes(), 2)


class CategoriePrix(models.Model):
    categorie = models.ForeignKey(CategorieFactureRecue, on_delete=models.CASCADE, related_name='categorie')
    # Prix TTC de cette catégorie
    prix = models.FloatField(default=0)
    facture = models.ForeignKey(FactureRecue, on_delete=models.CASCADE, related_name='categorie_prix')

    class Meta:
        db_table = 'treso2_categorieprix'
        constraints = [
            models.UniqueConstraint(fields=['categorie', 'facture'], name='unique categorie for facture')
        ]

class SousCategoriePrix(models.Model):
    sous_categorie = models.ForeignKey(SousCategorieFactureRecue, on_delete=models.CASCADE, related_name='sous_categorie')
    #Prix TTC de cette sous categorie
    prix = models.FloatField(default=0)
    facture = models.ForeignKey(FactureRecue, on_delete=models.CASCADE, related_name='sous_categorie_prix')

    class Meta:
        db_table = 'treso2_souscategorieprix'
        constraints = [
            models.UniqueConstraint(fields=['sous_categorie', 'facture'], name='unique sous categorie for facture')
        ]


class FactureEmise(models.Model):
    FACTURE_DUE = 'D'
    FACTURE_ANNULEE = 'A'
    FACTURE_PARTIELLEMENT_PAYEE = 'T'
    FACTURE_PAYEE = 'P'

    FACTURE_STATES = (
        (FACTURE_DUE, 'Due'),
        (FACTURE_ANNULEE, 'Annulée'),
        (FACTURE_PARTIELLEMENT_PAYEE, 'Partiellement payée'),
        (FACTURE_PAYEE, 'Payée'),
    )

    tva = models.FloatField(default=0)  # TVA en decimal, type 5.5, 20...
    prix = models.FloatField(default=0)  # prix TTC
    destinataire = models.CharField(max_length=255)
    date_creation = models.DateField(null=True, default=datetime.date.today())
    nom_createur = models.CharField(max_length=255)
    date_paiement = models.DateField(null=True)
    date_due = models.DateField()
    etat = models.CharField(max_length=1, choices=FACTURE_STATES)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, null=True, default=get_current_semester, related_name="semestre_actuelle")

    def get_price_without_taxes(self):
        """ À partir du prix TTC sauvegardé de l'objet, obtenir le prix HT """
        return round(self.prix * (100 / (100 + self.tva)), 2)

    def get_total_taxes(self):
        """ À partir du prix TTC sauvegardé de l'objet, obtenir la TVA """
        return round(self.prix - self.get_price_without_taxes(), 2)

@receiver(models.signals.pre_save, sender=FactureRecue)
def check_value_categorie_prix(sender, instance, **kwargs):
    if(CategoriePrix.objects.filter(facture_id=instance.id).exists()):
        prix=instance.prix
        total_categorie_prix = 0
        categories_prix = CategoriePrix.objects.filter(facture_id=instance.id)
        for categorie_prix in categories_prix:
            total_categorie_prix+=categorie_prix.prix
        if(prix!=total_categorie_prix):
            raise Exception(f'La somme total des prix des catégories est différente du prix total de la facture! \n Le prix total est {prix} et la somme des prix de vos categories est {total_categorie_prix}')


@receiver(models.signals.post_save, sender=FactureRecue)
def auto_add_facture_number_on_save(sender, instance, **kwargs):

    if instance.id and not instance.facture_number:

        # Assignement des numéros de factures à partir du début du semestre P20, facture 2563
        if CategoriePrix.objects.filter(facture_id=instance.id).exists():
            code = ""
            categories = CategoriePrix.objects.filter(facture_id=instance.id)
            for categorie in categories:
                cat = CategorieFactureRecue.objects.get(pk=categorie.categorie_id)
                code += cat.code
            queryset = Semestre.objects.get(pk=instance.semestre_id)
            semestre = queryset.periode + str(queryset.annee)
            instance.facture_number = semestre + "-" + code + str(instance.id)
            models.signals.post_save.disconnect(auto_add_facture_number_on_save, sender=FactureRecue)
            instance.save()
            models.signals.post_save.connect(auto_add_facture_number_on_save, sender=FactureRecue)


class Cheque(models.Model):
    CHEQUE_ENCAISSE = 'E'
    CHEQUE_PENDING = 'P'
    CHEQUE_ANNULE = 'A'
    CHEQUE_CAUTION = 'C'

    CHEQUE_STATES = (
        (CHEQUE_ENCAISSE, 'Encaisse'),
        (CHEQUE_PENDING, 'En cours'),
        (CHEQUE_ANNULE, 'Annulé'),
        (CHEQUE_CAUTION, 'Caution'),
    )

    num = models.IntegerField()
    valeur = models.FloatField(default=0)
    state = models.CharField(max_length=1, choices=CHEQUE_STATES)
    destinataire = models.CharField(max_length=255, null=True, default=None)
    date_encaissement = models.DateField(null=True)
    date_emission = models.DateField(null=True)
    commentaire = models.TextField(null=True, default=None)
    facture = models.ForeignKey(FactureRecue, on_delete=models.CASCADE, null=True, related_name='cheque')

class SuivieModificationFacture(models.Model):
    CREATION = 'C'
    SUPPRETION = 'S'
    MIS_A_JOUR = 'M'

    ACTION_CHOICES = (
        (CREATION, 'Creation de la facture'),
        (SUPPRETION, 'Suppretion de la facture'),
        (MIS_A_JOUR, 'Mis a jour de la facture')
    )

    facuture_number = models.TextField(null=True, blank=True, default=None)
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    login = models.CharField(max_length=16)
    date_creation = models.DateTimeField(null=True, default=datetime.datetime.now())