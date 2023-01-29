from django.db import models

from core.models import Semestre


class Sales(models.Model):
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField()
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    total_price = models.FloatField()
    semester_id = models.ForeignKey(Semestre, on_delete=models.CASCADE)


"""
WIP

class Supply(models.Model):
    id = models.BigAutoField(primary_key=True)
    supply_date = models.DateField(auto_now_add=True)
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    capacity = models.FloatField()
    unit = models.CharField(max_length=10)
    total_price = models.FloatField()
    semester_id = models.ForeignKey(Semestre, on_delete=models.CASCADE)
"""
