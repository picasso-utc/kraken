# Generated by Django 2.2.3 on 2019-09-09 09:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('perm', '0004_auto_20190904_1815'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signature',
            name='perm',
        ),
        migrations.AddField(
            model_name='signature',
            name='creneau',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='perm.Creneau'),
        ),
    ]