from django.db import models


class GoodiesWinner(models.Model):
    winner = models.CharField(max_length=50, unique=False)
    picked_up = models.BooleanField(default=False)

