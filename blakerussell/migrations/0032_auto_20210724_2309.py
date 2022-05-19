# Generated by Django 3.1.6 on 2021-07-25 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blakerussell', '0031_auto_20210724_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='capexfees',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='property',
            name='estimatedrent',
            field=models.IntegerField(blank=True, default='20'),
        ),
        migrations.AddField(
            model_name='property',
            name='hoafees',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='property',
            name='insurancefees',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='property',
            name='interestrate',
            field=models.FloatField(blank=True, default='5.0'),
        ),
        migrations.AddField(
            model_name='property',
            name='leaserate',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='property',
            name='notes',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='property',
            name='otherfees',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='property',
            name='pmrate',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='property',
            name='repairfees',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='property',
            name='vacancyrate',
            field=models.FloatField(blank=True, default='8.0'),
        ),
    ]
