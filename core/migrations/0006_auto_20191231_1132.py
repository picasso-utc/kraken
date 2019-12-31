# Generated by Django 2.2.3 on 2019-12-31 10:32

import core.services.current_semester
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20191023_2221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='semester',
        ),
        migrations.AddField(
            model_name='member',
            name='semestre',
            field=models.ForeignKey(default=core.services.current_semester.get_current_semester, on_delete=django.db.models.deletion.CASCADE, to='core.Semestre'),
        ),
    ]
