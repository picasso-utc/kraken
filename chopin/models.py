from django.db import models

# Create your models here.
from core.models import UserRight


class Newsletter(models.Model):
    id = models.BigAutoField(primary_key=True)
    author_id = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now=True)
    publication_date = models.DateTimeField()
    content = models.TextField()
