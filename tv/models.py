from django.db import models


class WebTVLink(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(max_length=200)


class WebTV(models.Model):
    name = models.CharField(max_length=30)
    link = models.ForeignKey(WebTVLink, on_delete=models.SET_NULL, null=True, default=None)


class WebTVMedia(models.Model):

    MEDIA_TYPE_CHOICES = (
        ('I', 'Image'),
        ('V', 'Video'),
    )

    name = models.CharField(max_length=50)
    media_type = models.CharField(choices=MEDIA_TYPE_CHOICES, default='I', max_length=1)
    media = models.FileField(upload_to="tv", null=True, blank=True, default=None)
    activate = models.BooleanField(default=False)
    times = models.IntegerField(default=1)