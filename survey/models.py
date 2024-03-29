import os

from django.db import models
from django.dispatch import receiver


class Survey(models.Model):

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="survey", null=True, blank=True, default=None)
    description = models.TextField()
    visible = models.BooleanField(default=False)
    multi_choice = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    total_votes = models.IntegerField(default=0)

@receiver(models.signals.post_delete, sender=Survey)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Suppression du fichier de l'attribut image à la suppresion
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=Survey)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Au moment d'une mise à jour, si l'image est différente
    suppression de l'ancienne
    """
    if not instance.pk:
        return False
    try:
        old_file = Survey.objects.get(pk=instance.pk).image
    except Survey.DoesNotExist:
        return False
    new_file = instance.image
    if old_file:
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)


class SurveyItem(models.Model):

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="survey", null=True, blank=True, default=None)
    description = models.TextField(blank=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)

@receiver(models.signals.post_delete, sender=SurveyItem)
def auto_delete_file_item_on_delete(sender, instance, **kwargs):
    """
    Suppression du fichier de l'attribut image à la suppresion
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=SurveyItem)
def auto_delete_file_item_on_change(sender, instance, **kwargs):
    """
    Au moment d'une mise à jour, si l'image est différente
    suppression de l'ancienne
    """
    if not instance.pk:
        return False
    try:
        old_file = SurveyItem.objects.get(pk=instance.pk).image
    except SurveyItem.DoesNotExist:
        return False
    new_file = instance.image
    if old_file:
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)


class SurveyItemVote(models.Model):

    login = models.CharField(max_length=10)
    survey_item = models.ForeignKey(SurveyItem, on_delete=models.CASCADE)
