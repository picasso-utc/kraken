from django.db import models


class Newsletter(models.Model):
    id = models.BigAutoField(primary_key=True)
    author_id = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now=True)
    publication_date = models.DateTimeField()
    content = models.TextField()

class Calendar(models.Model):
    nom = models.CharField(max_length=255)
    date = models.DateField()
    periode = models.TextField(null=True, default=None)

    def __str__(self):
        return f"{self.nom}"

