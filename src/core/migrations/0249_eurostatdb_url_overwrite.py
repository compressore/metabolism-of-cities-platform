# Generated by Django 3.0.6 on 2020-08-11 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0248_course_faq'),
    ]

    operations = [
        migrations.AddField(
            model_name='eurostatdb',
            name='url_overwrite',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
