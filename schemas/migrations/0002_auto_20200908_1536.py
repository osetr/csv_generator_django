# Generated by Django 3.0.5 on 2020-09-08 15:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schemas", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schema",
            name="date",
            field=models.DateTimeField(
                default=datetime.datetime(2020, 9, 8, 15, 36, 2, 732031), editable=False
            ),
        ),
    ]
