# Generated by Django 3.1.6 on 2021-07-24 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blakerussell', '0023_auto_20210724_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='zestimate',
            field=models.CharField(blank=True, default='0', max_length=15),
        ),
    ]
