# Generated by Django 3.1.6 on 2021-07-23 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blakerussell', '0010_auto_20210722_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='apistore',
            name='address',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='bathrooms',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='bedrooms',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='homesize',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='lotsize',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='state',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='yearbuilt',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='zestimate',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='apistore',
            name='zipcode',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
