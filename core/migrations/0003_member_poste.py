# Generated by Django 2.2.3 on 2019-10-23 11:40

import core.services.current_semester
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190902_0033'),
    ]

    operations = [
        migrations.CreateModel(
            name='Poste',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('name', models.CharField(max_length=25, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.CharField(max_length=50, null=True)),
                ('poste', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Poste')),
                ('semester', models.ForeignKey(default=core.services.current_semester.get_current_semester, on_delete=django.db.models.deletion.CASCADE, to='core.Semestre')),
                ('userright', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.UserRight')),
            ],
        ),
    ]
