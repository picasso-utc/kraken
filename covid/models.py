from django.db import models

class Table(models.Model):

    POSITION_CHOICES = (
        ('IN', 'Intérieur'),
        ('EXT', 'Extérieur'),
    )

    name = models.CharField(max_length=3)
    position = models.CharField(choices=POSITION_CHOICES, max_length=3)
    capacite = models.IntegerField()

class Person(models.Model):
    login = models.CharField(max_length=150)
    arrivee = models.DateTimeField(auto_now_add=True, blank=True)
    depart = models.DateTimeField(blank=True, null=True, default=None)
    table = models.ForeignKey(Table, on_delete=models.DO_NOTHING)
