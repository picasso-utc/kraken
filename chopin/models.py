from django.db import models


class Calendar(models.Model):
    nom = models.CharField(max_length=255)
    date = models.DateField()
    periode = models.TextField(null=True, default=None)

    def __str__(self):
        return f"{self.nom}"


class Newsletter(models.Model):
    semaine = models.DateField()
    contenu = models.TextField()

    def __str__(self):
        return f"{self.contenu}"