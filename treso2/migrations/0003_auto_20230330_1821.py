# Generated by Django 3.2.16 on 2023-03-30 16:21

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('treso2', '0002_auto_20230330_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='factureemise',
            name='date_creation',
            field=models.DateField(default=datetime.date(2023, 3, 30), null=True),
        ),
        migrations.AlterField(
            model_name='facturerecue',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 30, 18, 21, 26, 175141), null=True),
        ),
        migrations.CreateModel(
            name='Cheque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField()),
                ('valeur', models.FloatField(default=0)),
                ('state', models.CharField(choices=[('E', 'Encaisse'), ('P', 'En cours'), ('A', 'Annulé'), ('C', 'Caution')], max_length=1)),
                ('destinataire', models.CharField(default=None, max_length=255, null=True)),
                ('date_encaissement', models.DateField(null=True)),
                ('date_emission', models.DateField(null=True)),
                ('commentaire', models.TextField(default=None, null=True)),
                ('facturerecue', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cheque', to='treso2.facturerecue')),
            ],
        ),
    ]
