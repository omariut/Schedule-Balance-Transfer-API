# Generated by Django 3.2.1 on 2022-07-09 05:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transfer',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 9, 11, 27, 29, 914200)),
        ),
    ]
