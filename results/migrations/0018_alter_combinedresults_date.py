# Generated by Django 5.0.3 on 2024-05-16 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0017_raceresults_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='combinedresults',
            name='date',
            field=models.DateField(),
        ),
    ]
