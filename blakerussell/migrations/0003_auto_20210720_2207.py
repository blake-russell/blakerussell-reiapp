# Generated by Django 3.1.6 on 2021-07-21 03:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blakerussell', '0002_auto_20210720_2204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='owned',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned', to=settings.AUTH_USER_MODEL),
        ),
    ]
