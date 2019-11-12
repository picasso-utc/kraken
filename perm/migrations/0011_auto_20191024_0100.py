# Generated by Django 2.2.3 on 2019-10-23 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perm', '0010_auto_20191023_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='astreinte',
            name='commentaire',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='astreinte',
            name='note_anim',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='astreinte',
            name='note_deco',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='astreinte',
            name='note_menu',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='astreinte',
            name='note_orga',
            field=models.IntegerField(default=0),
        ),
    ]