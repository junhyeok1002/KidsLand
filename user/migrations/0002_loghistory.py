# Generated by Django 4.2.7 on 2023-11-29 13:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LogHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.TextField()),
                ("is_OK", models.TextField()),
                ("child_name", models.TextField()),
                ("child_birth", models.TextField()),
                ("reservation_date", models.TextField()),
                ("reservation_time", models.TextField()),
                ("parents_number", models.TextField()),
                ("status", models.TextField()),
            ],
        ),
    ]
