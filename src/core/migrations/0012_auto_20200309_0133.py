# Generated by Django 3.0.3 on 2020-03-09 01:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20200307_0708'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ['position', 'title']},
        ),
    ]
