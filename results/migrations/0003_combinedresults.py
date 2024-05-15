# Generated by Django 5.0.3 on 2024-04-04 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0002_raceresults"),
    ]

    operations = [
        migrations.CreateModel(
            name="CombinedResults",
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
                ("title", models.CharField(max_length=255)),
                ("boden", models.CharField(max_length=100)),
                ("reiter", models.CharField(max_length=100)),
                ("abstand", models.CharField(blank=True, max_length=100, null=True)),
                ("abstand_zeit", models.FloatField(blank=True, null=True)),
                ("race_time", models.CharField(blank=True, max_length=100, null=True)),
                ("date", models.DateField()),
                ("box", models.CharField(max_length=100, null=True)),
                ("ort", models.CharField(max_length=100)),
                ("strs", models.IntegerField(blank=True, null=True)),
                ("distanz", models.IntegerField(blank=True, null=True)),
                ("kategorie", models.CharField(max_length=100)),
                ("platz", models.IntegerField(blank=True, null=True)),
                ("gew", models.FloatField(blank=True, null=True)),
                ("gag", models.FloatField(blank=True, null=True)),
                ("evq", models.FloatField(blank=True, null=True)),
                ("horse_id", models.CharField(max_length=255)),
                ("race_id", models.CharField(max_length=255)),
                ("race_horse_id", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "馬柱",
                "verbose_name_plural": "馬柱",
                "db_table": "combinedresults",
            },
        ),
    ]
