# Generated by Django 3.1.6 on 2021-07-24 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blakerussell', '0025_property_downpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='av_cost_of_living',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='property',
            name='av_crime',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='property',
            name='av_employment',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='property',
            name='av_housing',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='property',
            name='av_livability',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='property',
            name='av_schools',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='property',
            name='av_user_ratings',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]