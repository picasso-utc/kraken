# Generated by Django 2.2.3 on 2020-01-15 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20191231_1132'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('badge_uid', models.CharField(default=None, max_length=10, unique=True)),
                ('justification', models.CharField(default=None, max_length=255)),
            ],
        ),
    ]
