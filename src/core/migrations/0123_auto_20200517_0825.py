# Generated by Django 3.0.3 on 2020-05-17 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0122_auto_20200517_0810'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='is_internal',
        ),
        migrations.RemoveField(
            model_name='project',
            name='site',
        ),
        migrations.RemoveField(
            model_name='project',
            name='url',
        ),
        migrations.AddField(
            model_name='project',
            name='has_subsite',
            field=models.BooleanField(default=False),
        ),
    ]
