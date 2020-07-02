# Generated by Django 3.0.6 on 2020-07-02 06:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0215_auto_20200702_0524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='catalog',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='core.MaterialCatalog'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='parent_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.Tag'),
        ),
    ]
