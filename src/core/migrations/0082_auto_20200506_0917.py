# Generated by Django 3.0.3 on 2020-05-06 09:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0081_auto_20200506_0513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryitem',
            name='language',
            field=models.CharField(choices=[('EN', 'English'), ('ES', 'Spanish'), ('CH', 'Chinese'), ('FR', 'French'), ('GE', 'German'), ('NL', 'Dutch'), ('OT', 'Other')], default='EN', max_length=2),
        ),
        migrations.AlterField(
            model_name='people',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
