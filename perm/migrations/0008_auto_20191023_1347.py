# Generated by Django 2.2.3 on 2019-10-23 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perm', '0007_astreinte'),
    ]

    operations = [
        migrations.AlterField(
            model_name='astreinte',
            name='astreinte_type',
            field=models.CharField(choices=[('M1', 'Matin1'), ('M2', 'Matin2'), ('D1', 'Déjeuner1'), ('D2', 'Déjeuner2'), ('S', 'Soir')], max_length=2),
        ),
    ]