# Generated by Django 5.0.3 on 2024-04-14 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0009_alter_raceresults_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="combinedresults",
            name="this_race_nr",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="raceresults",
            name="this_race_nr",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
