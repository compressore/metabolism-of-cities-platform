# Generated by Django 3.0.3 on 2020-03-13 12:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_articledesign_custom_css'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='articledesign',
            name='color',
        ),
        migrations.RemoveField(
            model_name='articledesign',
            name='header_texture',
        ),
    ]
