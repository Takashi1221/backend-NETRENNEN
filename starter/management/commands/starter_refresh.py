import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.conf import settings
from django.utils.timezone import make_aware, get_current_timezone
from datetime import datetime
import pandas as pd
import re
import numpy as np
from tqdm import tqdm 
import random
from io import StringIO
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch
from asgiref.sync import sync_to_async
from starter.models import Renntermine, Starter


# 環境変数DEBUGを設定
os.environ['DEBUG'] = 'puppeteer:*'
# ログの設定
logging.basicConfig(level=logging.DEBUG, filename='/tmp/pyppeteer.log', filemode='w')


class Command(BaseCommand):
    help = 'Refresh starters and update database'
    
    async def wait_randomly(self, min_seconds, max_seconds):

        wait_time = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(wait_time)


    async def get_starter(self):
        
        raceids = await sync_to_async(set)(Renntermine.objects.values_list('race_id', flat=True))
        
        return raceids

    async def starter(self, raceids):
        starter_dfs = {}
        for raceid in raceids:
            try:
                browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-software-rasterizer'], dumpio=True)
                page = await browser.newPage()
                await page.setViewport({'width': 1920, 'height': 1080})
                await page.goto("https://www.deutscher-galopp.de/gr/renntage/rennen.php?id=" + raceid)
                await self.wait_randomly(1, 5)
                
                table_html = await page.evaluate(  # 出馬予定表のテーブルを取得
                    '''() => {
                        const table = document.querySelector('#nennungen'); 
                        return table ? table.outerHTML : null;
                    }'''
                )
                await browser.close()

                df = pd.DataFrame()
                if table_html:
                    table_io = StringIO(table_html)
                    dfs = pd.read_html(table_io)
                    if dfs:
                        df = dfs[0] 
                        df = df.drop(df.index[-1])  # 余分な行があるので落とす
                        df["raceid"] = raceid
                        
                        soup = BeautifulSoup(table_html, 'html.parser')
                        a_tags = soup.select('table#nennungen a')
                        id_regex = re.compile(r'/pferd/(\d+)/')
                        horse_ids = [id_regex.search(a['href']).group(1) for a in a_tags if id_regex.search(a['href'])]
                        df["horse_id"] = horse_ids
                        starter_dfs[raceid] = df
                    else:
                        logger.error("テーブルが見つかりませんでした。") # 基本的にこのテーブルはあります
                        
            except Exception as e:
                logging.error(f'Error during Pyppeteer task: {e}')  # エラーメッセージをログに記録
                raise
            
        starter_df = pd.concat(starter_dfs.values()).reset_index(drop=True)
        return starter_df
    

    async def main(self):

        raceids = await self.get_starter()
        starter_df = await self.starter(raceids)

        # 初期化してから出走馬一覧を追加
        await sync_to_async(Starter.objects.all().delete)()
        for _, row in starter_df.iterrows():
            box_value = row.get('Box', '-') # 'Box'列がない場合
            await sync_to_async(Starter.objects.create, thread_sensitive=True)(
            number=row['Nr.'],
            name=row['Name'],
            gag=row['GAG'],
            box=box_value,  # 取得した値（またはデフォルト値）を使用,
            alter=row['Alter'],
            owner=row['Besitzer'],
            trainer=row['Trainer'],
            jocky=row['Reiter'],
            gew=row['Gew.'],
            race_id=row['raceid'],
            horse_id=row['horse_id']
            )
                                       
    
    def handle(self, *args, **options):
        # asyncio.run() で非同期処理を同期的に実行
        asyncio.run(self.main())
