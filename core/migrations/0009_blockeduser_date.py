# Generated by Django 2.2.3 on 2020-01-15 11:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_blockeduser_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockeduser',
            name='date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]