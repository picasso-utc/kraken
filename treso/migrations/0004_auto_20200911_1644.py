# Generated by Django 2.2.3 on 2020-09-11 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treso', '0003_auto_20200216_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facturerecue',
            name='moyen_paiement',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AlterField(
            model_name='facturerecue',
            name='personne_a_rembourser',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
