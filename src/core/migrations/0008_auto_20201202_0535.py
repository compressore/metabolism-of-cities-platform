# Generated by Django 3.1.2 on 2020-12-02 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20201122_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='measurement_type',
            field=models.IntegerField(blank=True, choices=[(1, 'Mass'), (2, 'Volume'), (3, 'Count'), (4, 'Area'), (5, 'Energy'), (6, 'Length'), (7, 'Fraction'), (8, 'Power'), (99, 'Other')], db_index=True, default=1, null=True),
        ),
        migrations.AlterField(
            model_name='unit',
            name='type',
            field=models.IntegerField(choices=[(1, 'Mass'), (2, 'Volume'), (3, 'Count'), (4, 'Area'), (5, 'Energy'), (6, 'Length'), (7, 'Fraction'), (8, 'Power'), (99, 'Other')], db_index=True, default=99),
        ),
    ]
