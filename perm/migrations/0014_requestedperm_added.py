# Generated by Django 2.2.3 on 2019-12-20 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perm', '0013_auto_20191215_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestedperm',
            name='added',
            field=models.BooleanField(default=False),
        ),
    ]