# Generated by Django 3.1.6 on 2021-07-23 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blakerussell', '0011_auto_20210722_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apistore',
            name='bathrooms',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='apistore',
            name='bedrooms',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='apistore',
            name='homesize',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='apistore',
            name='lotsize',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='apistore',
            name='state',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='apistore',
            name='yearbuilt',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='apistore',
            name='zestimate',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='apistore',
            name='zipcode',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='bathrooms',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='property',
            name='bedrooms',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='property',
            name='homesize',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='lotsize',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='zestimate',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
