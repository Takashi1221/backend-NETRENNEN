import csv
from django.core.management.base import BaseCommand
from pathlib import Path
from datetime import datetime
from starter.models import KalenderModel

class Command(BaseCommand):
    help = 'Load a list of races from a CSV file into the database'

    def handle(self, *args, **options):
        path = Path('kalender2024.csv')  # CSVファイルのパス
        with path.open('r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # ヘッダー行をスキップ
            for row in reader:
                datum = datetime.strptime(row[0], '%d.%m.%y')  # 日付の形式を変更
                _, created = KalenderModel.objects.get_or_create(
                    datum=datum,
                    rennort=row[1],
                    renntitel=row[2],
                    distanz=row[3],
                    kategorie=row[4],
                    stute=row[5],
                    preisgeld=row[6],
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully added race {row[2]}'))