from django.db import models

class Survey(models.Model):

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="survey", null=True, blank=True, default=None)
    description = models.TextField()
    visible = models.BooleanField(default=False)
    multi_choice = models.BooleanField(default=False)


class SurveyItem(models.Model):

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="survey", null=True, blank=True, default=None)
    description = models.TextField()
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)


class SurveyItemVote(models.Model):

    login = models.CharField(max_length=10)
    survey_item = models.ForeignKey(SurveyItem, on_delete=models.CASCADE)
