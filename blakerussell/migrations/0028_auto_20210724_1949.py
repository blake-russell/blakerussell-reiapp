# Generated by Django 3.1.6 on 2021-07-25 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blakerussell', '0027_auto_20210724_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='av_cost_of_living',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='av_crime',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='av_employment',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='av_housing',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='av_schools',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AlterField(
            model_name='property',
            name='av_user_ratings',
            field=models.CharField(blank=True, max_length=5),
        ),
    ]
