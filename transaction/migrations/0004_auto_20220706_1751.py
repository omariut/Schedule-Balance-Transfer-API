# Generated by Django 3.2.1 on 2022-07-06 11:51

import datetime
from django.db import migrations, models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('transaction', '0003_auto_20220706_1744'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transactionhistory',
            options={'ordering': ['-created_at'], 'verbose_name': 'Transaction Historie'},
        ),
        migrations.AlterField(
            model_name='account',
            name='balance',
            field=models.FloatField(validators=[utils.validators.validate_positive_amount]),
        ),
        migrations.AlterField(
            model_name='transfer',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 6, 17, 51, 24, 384472)),
        ),
    ]