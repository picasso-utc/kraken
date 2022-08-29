from django.db import models


class Creneau(models.Model):
    id = models.BigAutoField(primary_key=True)
    shotgunDate = models.DateTimeField(default=None)
    max_people = models.IntegerField(default=25)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    text = models.CharField(max_length=250)
    actif = models.BooleanField(default=True)


class UserInShotgun(models.Model):
    id = models.BigAutoField(primary_key=True)
    login = models.CharField(max_length=30)
    email = models.CharField(max_length=150, null=True)
    id_creneau = models.ForeignKey(Creneau, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = (("id_creneau", "login"),)
