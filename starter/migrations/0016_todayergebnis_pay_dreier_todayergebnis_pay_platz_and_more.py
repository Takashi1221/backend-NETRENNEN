# Generated by Django 5.0.3 on 2024-06-25 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starter', '0015_alter_starter_equip_alter_starter_erlbnis'),
    ]

    operations = [
        migrations.AddField(
            model_name='todayergebnis',
            name='pay_dreier',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='todayergebnis',
            name='pay_platz',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='todayergebnis',
            name='pay_sieg',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='todayergebnis',
            name='pay_zweier',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
