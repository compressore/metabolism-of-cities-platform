# Generated by Django 3.0.6 on 2020-06-23 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0180_eurostatdb_has_no_meta_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='eurostatdb',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
