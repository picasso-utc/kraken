from django.db import models
from perm.models import Perm, Creneau
from core.models import Semestre
from core.services.current_semester import get_current_semester
from django.dispatch import receiver


class PricedModel(models.Model):
    """
    Classe abstraite qui représente tout objet qui a un prix.
    """
    tva = models.FloatField(default=0) # TVA en decimal, type 5.5, 20...
    prix = models.FloatField(default=0) # prix TTC

    def get_price_without_taxes(self):
        """ À partir du prix TTC sauvegardé de l'objet, obtenir le prix HT """
        return round(self.prix * (100 / (100 + self.tva)), 2)

    def get_total_taxes(self):
        """ À partir du prix TTC sauvegardé de l'objet, obtenir la TVA """
        return round(self.prix - self.get_price_without_taxes(), 2)

    class Meta:
        """ Représentation en DB """
        abstract = True


class CategorieFactureRecue(models.Model):
    nom = models.CharField(max_length=255)
    code = models.CharField(max_length=1, unique=True)


class FactureRecue(PricedModel):

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

    perm = models.ForeignKey(Creneau, on_delete=models.CASCADE, null=True, default=None)
    etat = models.CharField(max_length=1, choices=FACTURE_STATES, default=FACTURE_A_PAYER)
    categorie = models.ForeignKey(CategorieFactureRecue, on_delete=models.CASCADE, null=True)
    nom_entreprise = models.CharField(max_length=255)
    date = models.DateField()
    date_paiement = models.DateField(null=True, default=None)
    date_remboursement = models.DateField(null=True, default=None)
    moyen_paiement = models.CharField(null=True, default=None, max_length=255)
    personne_a_rembourser = models.CharField(null=False, default=None, max_length=255)
    immobilisation = models.BooleanField(default=False)
    remarque = models.TextField(null=True, default=None)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, null=True, default=get_current_semester)
    facture_number = models.TextField(null=True, blank=True, default=None)

@receiver(models.signals.post_save, sender=FactureRecue)
def auto_add_facture_number_on_save(sender, instance, **kwargs):
    if instance.id:
        # Assignement des numéros de factures à partir du début du semestre P20, facture 2563
        if instance.id > 2563:
            code = "" 
            if instance.categorie:
                queryset = CategorieFactureRecue.objects.get(pk=instance.categorie_id)
                code = queryset.code
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
    facturerecue = models.ForeignKey(FactureRecue, on_delete=models.CASCADE, null=True)


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

    destinataire = models.CharField(max_length=255)
    date_creation = models.DateField(auto_now_add=True)
    nom_createur = models.CharField(max_length=255)
    date_paiement = models.DateField(null=True)
    date_due = models.DateField()
    etat = models.CharField(max_length=1, choices=FACTURE_STATES)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, null=True, default=get_current_semester)

    def get_total_ht_price(self):
        rows = self.factureemiserow_set.all()
        return round(sum([row.get_total_ht_price() for row in rows]), 2)

    def get_total_ttc_price(self):
        rows = self.factureemiserow_set.all()
        return round(sum([row.get_total_ttc_price() for row in rows]), 2)


class FactureEmiseRow(PricedModel):
    facture = models.ForeignKey(FactureEmise, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    qty = models.IntegerField()

    def get_total_ttc_price(self):
        return self.prix * self.qty

    def get_total_ht_price(self):
        return self.qty * self.get_price_without_taxes()

    def get_total_taxes_for_row(self):
        return self.qty * self.get_total_taxes()


class ReversementEffectue(PricedModel):
    """
    Reversement incluant la TVA

    Note: le use case de ce modèle est le calcul du solde théorique sur le compte
    en banque du Pic (option "banque" sur le front). Actuellement, les utilisateurs
    rentrent à la main les reversements - les importer demanderait des process supplémentaires
    en termes d'identification du reversement, etc. Si des use cases de la sauvegarde des reversements
    s'y prêtent, il pourrait être intéressant de conserver plus d'infos (ID sur payutc, p.e.)
    mais il n'y a pas d'intérêt pour le moment.

    C'est un PricedModel mais il y a peu d'intérêt à conserver la TVA.
    """
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, null=True, default=get_current_semester)
    date_effectue = models.DateField(null=True) # Date a laquelle il fut effectue
