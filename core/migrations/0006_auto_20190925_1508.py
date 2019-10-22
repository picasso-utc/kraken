# Generated by Django 2.2.3 on 2019-09-25 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20190925_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='poste_id',
        ),
        migrations.AddField(
            model_name='member',
            name='poste_id',
            field=models.ManyToManyField(to='core.Poste'),
        ),
        migrations.RemoveField(
            model_name='member',
            name='semestre_id',
        ),
        migrations.AddField(
            model_name='member',
            name='semestre_id',
            field=models.ManyToManyField(to='core.Semestre'),
        ),
        migrations.RemoveField(
            model_name='member',
            name='userright_id',
        ),
        migrations.AddField(
            model_name='member',
            name='userright_id',
            field=models.ManyToManyField(to='core.UserRight'),
        ),
    ]
