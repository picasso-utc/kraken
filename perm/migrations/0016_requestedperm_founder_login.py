# Generated by Django 2.2.3 on 2019-12-23 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perm', '0015_requestedperm_semestre'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestedperm',
            name='founder_login',
            field=models.CharField(default=None, max_length=8),
        ),
    ]
