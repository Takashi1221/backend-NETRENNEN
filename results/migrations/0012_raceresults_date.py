from django.db import migrations, models

def clear_horse_results_data(apps, schema_editor):
    HorseResults = apps.get_model('results', 'HorseResults')
    HorseResults.objects.all().delete()  # すべてのデータを削除

class Migration(migrations.Migration):

    dependencies = [
        ('results', '0011_alter_horseresults_evq_alter_horseresults_gag_and_more'),
    ]

    operations = [
        migrations.RunPython(clear_horse_results_data),  # データの削除
        migrations.AlterField(
            model_name='horseresults',
            name='date',
            field=models.DateField(),  # DateTimeField から DateField への変更
        ),
    ]