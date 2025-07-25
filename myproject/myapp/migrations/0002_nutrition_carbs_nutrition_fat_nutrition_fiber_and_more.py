# Generated by Django 5.2.4 on 2025-07-14 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="nutrition",
            name="carbs",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="nutrition",
            name="fat",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="nutrition",
            name="fiber",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="nutrition",
            name="protein",
            field=models.FloatField(default=0),
        ),
    ]
