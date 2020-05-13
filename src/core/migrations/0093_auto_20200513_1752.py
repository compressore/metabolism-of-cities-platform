# Generated by Django 3.0.3 on 2020-05-13 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0092_auto_20200513_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workactivity',
            name='type',
            field=models.IntegerField(choices=[(1, 'Creating'), (2, 'Uploading'), (3, 'Reviewing'), (4, 'Curating'), (5, 'Sharing'), (6, 'Participating'), (7, 'Learning'), (8, 'Administering'), (9, 'Programming'), (10, 'Designing')], db_index=True),
        ),
    ]
