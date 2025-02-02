# Generated by Django 3.1.2 on 2021-01-07 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20201222_0711'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalBusinessDependency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Local Business Dependencies',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='NaceCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='organization',
            name='updated_at',
            field=models.DateField(auto_now=True, null=True),
        ),
        migrations.CreateModel(
            name='LocalBusinessLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.organization')),
                ('dependence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.localbusinessdependency')),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='organization', to='core.organization')),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='nace_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.nacecode'),
        ),
    ]
