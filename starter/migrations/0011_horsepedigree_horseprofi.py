# Generated by Django 5.0.3 on 2024-04-17 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("starter", "0010_starter_horse_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="HorsePedigree",
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
                ("pedigree_1", models.CharField(max_length=100, verbose_name="父")),
                ("pedigree_2", models.CharField(max_length=100, verbose_name="母父")),
                ("pedigree_3", models.CharField(max_length=100)),
                ("pedigree_4", models.CharField(max_length=100)),
                ("pedigree_5", models.CharField(max_length=100, verbose_name="母母父")),
                ("pedigree_6", models.CharField(max_length=100)),
                ("pedigree_7", models.CharField(max_length=100)),
                ("pedigree_8", models.CharField(max_length=100)),
                ("pedigree_9", models.CharField(max_length=100)),
                ("pedigree_10", models.CharField(max_length=100)),
                ("pedigree_11", models.CharField(max_length=100)),
                ("pedigree_12", models.CharField(max_length=100)),
                ("pedigree_13", models.CharField(max_length=100)),
                ("pedigree_14", models.CharField(max_length=100)),
                ("pedigree_15", models.CharField(max_length=100)),
                ("pedigree_16", models.CharField(max_length=100)),
                ("pedigree_17", models.CharField(max_length=100)),
                ("pedigree_18", models.CharField(max_length=100)),
                ("pedigree_19", models.CharField(max_length=100)),
                ("pedigree_20", models.CharField(max_length=100)),
                ("pedigree_21", models.CharField(max_length=100)),
                ("pedigree_22", models.CharField(max_length=100)),
                ("pedigree_23", models.CharField(max_length=100)),
                ("pedigree_24", models.CharField(max_length=100)),
                ("pedigree_25", models.CharField(max_length=100)),
                ("pedigree_26", models.CharField(max_length=100)),
                ("pedigree_27", models.CharField(max_length=100)),
                ("pedigree_28", models.CharField(max_length=100)),
                ("pedigree_29", models.CharField(max_length=100)),
                ("pedigree_30", models.CharField(max_length=100)),
                ("sire_id", models.CharField(max_length=50)),
                ("dam_id", models.CharField(max_length=50)),
                ("horse_id", models.CharField(max_length=50, unique=True)),
            ],
            options={
                "verbose_name": "現役馬血統",
                "verbose_name_plural": "現役馬血統",
                "db_table": "horsepedigree",
            },
        ),
        migrations.CreateModel(
            name="HorseProfi",
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
                ("sex", models.CharField(max_length=100, verbose_name="性別")),
                (
                    "standort",
                    models.CharField(max_length=100, verbose_name="スタリオン"),
                ),
                ("trainer", models.CharField(max_length=100, verbose_name="調教師")),
                ("owner", models.CharField(max_length=100, verbose_name="馬主")),
                ("breeder", models.CharField(max_length=100, verbose_name="生産者")),
                ("family", models.CharField(max_length=50, verbose_name="牝系番号")),
                ("name", models.CharField(max_length=50, verbose_name="馬名")),
                ("birth", models.CharField(max_length=50, verbose_name="生まれ年")),
                (
                    "total_earnings",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="総獲得賞金"
                    ),
                ),
                (
                    "horse_id",
                    models.CharField(max_length=50, unique=True, verbose_name="馬ID"),
                ),
            ],
            options={
                "verbose_name": "馬プロフィール",
                "verbose_name_plural": "馬プロフィール",
                "db_table": "horseprofi",
            },
        ),
    ]
