# Generated by Django 4.2.7 on 2024-01-05 18:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0013_alter_task_due_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="due_date",
            field=models.DateField(default=datetime.date(2024, 1, 9)),
        ),
    ]
