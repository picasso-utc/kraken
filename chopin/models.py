from django.db import models
from core import models as core_models
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
