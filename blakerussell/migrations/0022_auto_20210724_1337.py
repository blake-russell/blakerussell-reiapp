# Generated by Django 3.1.6 on 2021-07-24 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blakerussell', '0021_property_tax_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='appraise_rate',
            field=models.CharField(blank=True, default='0', max_length=15),
        ),
        migrations.AlterField(
            model_name='property',
            name='tax_rate',
            field=models.CharField(blank=True, default='0', max_length=15),
        ),
    ]
