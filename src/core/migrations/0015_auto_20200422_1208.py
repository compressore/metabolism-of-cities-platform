# Generated by Django 3.0.3 on 2020-04-22 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_merge_20200422_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='email_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='people',
            name='firstname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='google_scholar',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='lastname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='linkedin',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='orcid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='research_interests',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='researchgate',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('retired', 'Retired'), ('deceased', 'Deceased'), ('inactive', 'Inactive'), ('pending', 'Pending Review')], default='active', max_length=8),
        ),
        migrations.AddField(
            model_name='people',
            name='twitter',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='website',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
