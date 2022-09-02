from django.db import models
from core import models as core_models
from perm import models as perm_models
from core.services.current_semester import get_current_semester


class Newsletter(models.Model):
    id = models.BigAutoField(primary_key=True)
    author_id = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now=True)
    publication_date = models.DateTimeField()
    content = models.TextField()


class Calendar(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    date = models.DateField()
    responsable = models.CharField(null=True, default=None, max_length=255)
    semestre = models.ForeignKey(core_models.Semestre, on_delete=models.SET_NULL, null=True,
                                 default=get_current_semester)
    description = models.TextField(null=True)
    periode = models.CharField(null=True, max_length=5)
    hour = models.TimeField(null=True)

    def __str__(self):
        return f"{self.nom}"


class TrendingProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom_produit = models.CharField(max_length=255)
    description = models.TextField(null=True)
    nom_categorie = models.CharField(max_length=255)


class PlanningTypeJour(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    description = models.TextField(null=True)


class PlanningCreneau(models.Model):
    id = models.BigAutoField(primary_key=True)
    hour = models.TimeField()
    duree = models.IntegerField()


class PlanningJob(models.Model):
    id = models.BigAutoField(primary_key=True)
    titre = models.CharField(max_length=255)
    description = models.TextField(null=True)


class PlanningCota(models.Model):
    id_creneau = models.ForeignKey(PlanningCreneau, on_delete=models.SET_NULL, null=True)
    id_typejour = models.ForeignKey(PlanningTypeJour, on_delete=models.SET_NULL, null=True)
    id_job = models.ForeignKey(PlanningJob, on_delete=models.SET_NULL, null=True)
    nb = models.IntegerField()


class PlanningMember(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_perm = models.ForeignKey(perm_models.Creneau, on_delete=models.SET_NULL, null=True)
    nom = models.CharField(max_length=255)


class PlanningRepartission(models.Model):
    id_creneau = models.ForeignKey(perm_models.Creneau, on_delete=models.SET_NULL, null=True)
    id_membre = models.ForeignKey(PlanningMember, on_delete=models.SET_NULL, null=True)
    id_job = models.ForeignKey(PlanningJob, on_delete=models.SET_NULL, null=True)