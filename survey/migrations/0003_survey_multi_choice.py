# Generated by Django 2.2.3 on 2019-11-05 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_survey_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='multi_choice',
            field=models.BooleanField(default=False),
        ),
    ]