import pandas as pd
from django.core.management.base import BaseCommand
from results.models import RaceResults
from starter.models import HorsePedigree
from django.db import transaction
from asgiref.sync import sync_to_async
import asyncio
import pickle

class Command(BaseCommand):
    help = 'temp update database'

    async def main(self):
        # RaceResultsからhorse_id, sire, damsireを取得
        race_results_qs = await sync_to_async(list)(RaceResults.objects.values('id', 'horse_id', 'sire', 'damsire'))
        race_results_df = pd.DataFrame(list(race_results_qs))

        # HorsePedigreeからhorse_id, pedigree_1, pedigree_2を取得
        pedigree_qs = await sync_to_async(list)(HorsePedigree.objects.values('horse_id', 'pedigree_1', 'pedigree_5'))
        pedigree_df = pd.DataFrame(list(pedigree_qs))

        # race_results_dfとpedigree_dfをhorse_idでマージ
        merged_df = pd.merge(race_results_df, pedigree_df, on="horse_id", how="left")

        # sireとdamsireを更新
        merged_df['sire'] = merged_df['pedigree_1']
        merged_df['damsire'] = merged_df['pedigree_5']
        
        await sync_to_async(self.update_database)(merged_df)
        
    def update_database(self, merged_df):
        with transaction.atomic():
            for _, row in merged_df.iterrows():
                RaceResults.objects.filter(id=row['id']).update(sire=row['sire'], damsire=row['damsire'])
        

    def handle(self, *args, **options):
        asyncio.run(self.main())