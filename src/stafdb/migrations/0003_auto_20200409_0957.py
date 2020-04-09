# Generated by Django 3.0.3 on 2020-04-09 09:57

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stafdb', '0002_material_materialcatalog'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceSpace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('slug', models.CharField(max_length=100, null=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='geocode',
            name='parent',
        ),
        migrations.AddField(
            model_name='geocode',
            name='depth',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='geocodesystem',
            name='is_comprehensive',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.CreateModel(
            name='ReferenceSpaceLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('start', models.DateField(blank=True, db_index=True, null=True)),
                ('end', models.DateField(blank=True, db_index=True, null=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stafdb.ReferenceSpace')),
            ],
            options={
                'ordering': ['-start'],
            },
        ),
        migrations.CreateModel(
            name='ReferenceSpaceGeocode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('geocode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stafdb.Geocode')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stafdb.ReferenceSpace')),
            ],
        ),
        migrations.AddField(
            model_name='referencespace',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='stafdb.ReferenceSpaceLocation'),
        ),
    ]
