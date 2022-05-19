# Generated by Django 3.1.6 on 2021-07-25 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blakerussell', '0032_auto_20210724_2309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='capexfees',
            field=models.CharField(blank=True, default='8', max_length=15),
        ),
        migrations.AlterField(
            model_name='property',
            name='leaserate',
            field=models.CharField(blank=True, default='8', max_length=15),
        ),
        migrations.AlterField(
            model_name='property',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=2000),
        ),
        migrations.AlterField(
            model_name='property',
            name='pmrate',
            field=models.CharField(blank=True, default='8', max_length=15),
        ),
        migrations.AlterField(
            model_name='property',
            name='repairfees',
            field=models.CharField(blank=True, default='8', max_length=15),
        ),
    ]