# Generated by Django 2.2.3 on 2021-09-04 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chopin', '0004_planningcota_planningcreneau_planningjob_planningmember_planningrepartission_planningtypejour'),
    ]

    operations = [
        migrations.RenameField(
            model_name='planningjob',
            old_name='descroption',
            new_name='description',
        ),
    ]
