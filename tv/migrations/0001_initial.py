# Generated by Django 2.2.3 on 2019-10-02 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WebTV',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('location', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='TVConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(blank=True, default=None, max_length=500, null=True)),
                ('photo', models.ImageField(blank=True, default=None, null=True, upload_to='photos')),
                ('enable_messages', models.BooleanField(default=False)),
                ('is_image', models.BooleanField(default=False)),
                ('tv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tv.WebTV')),
            ],
        ),
    ]
