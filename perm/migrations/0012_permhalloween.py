# Generated by Django 2.2.3 on 2019-10-27 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perm', '0011_auto_20191024_0100'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermHalloween',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article_id', models.IntegerField(default=0)),
                ('login', models.CharField(default=None, max_length=10, null=True)),
            ],
        ),
    ]