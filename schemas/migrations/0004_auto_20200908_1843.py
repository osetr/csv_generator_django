# Generated by Django 3.0.5 on 2020-09-08 15:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ("schemas", "0003_auto_20200908_1537"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schema",
            name="date",
            field=models.DateTimeField(
                default=datetime.datetime(2020, 9, 8, 15, 43, 26, 700238, tzinfo=utc),
                editable=False,
            ),
        ),
    ]
