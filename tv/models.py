from django.db import models
import os
from django.dispatch import receiver

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


@receiver(models.signals.post_delete, sender=WebTVMedia)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Suppression du fichier de l'attribut image à la suppresion
    """
    if instance.media:
        if os.path.isfile(instance.media.path):
            os.remove(instance.media.path)

@receiver(models.signals.pre_save, sender=WebTVMedia)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Au moment d'une mise à jour, si l'image est différente
    suppression de l'ancienne
    """
    if not instance.pk:
        return False
    try:
        old_file = WebTVMedia.objects.get(pk=instance.pk).media
    except WebTVMedia.DoesNotExist:
        return False
    new_file = instance.media
    if old_file:
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)