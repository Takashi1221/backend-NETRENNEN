import asyncio
from asgiref.sync import sync_to_async
from datetime import datetime, time
from django.core.management.base import BaseCommand
from pyppeteer import launch
import re
from starter.models import Renntermine, TodayErgebnis, TodayOdds

class Command(BaseCommand):
    help = 'Scrapes odds data and results'

    async def main(self):
        # スクリプト実行日の日付を取得
        today = datetime.today().date()

        # Renntermineモデルから現在の日付と一致するレコードを取得
        race_ids = await sync_to_async(list)(Renntermine.objects.filter(date=today).values_list('race_id', flat=True))

        # 一致するレコードがない場合はスクリプトを終了
        if not race_ids:
            await self.clear_today_records()
            self.stdout.write(self.style.WARNING('No races found for today. Exiting script.'))
            return

        # 現在の時刻を取得
        current_time = datetime.now().time()

        # 現在時刻が午前8時から午後9時の間であるかを確認
        if time(8, 0) <= current_time <= time(21, 0):
            # race_idを使用してスクレイピングする（ここはコードが未定なので省略）
            await self.scrape_races(race_ids)
        else:
            self.stdout.write(self.style.WARNING('Current time is outside of the allowed range.'))
            
    async def clear_today_records(self):
        await sync_to_async(TodayErgebnis.objects.all().delete)()
        await sync_to_async(TodayOdds.objects.all().delete)()
        self.stdout.write(self.style.SUCCESS('Cleared TodayErgebnis and TodayOdds records.'))


    async def scrape_races(self, race_ids):
        # スクレイピングのロジックをここに実装
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-software-rasterizer'], dumpio=True)
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})
        
        # Cookie承諾画面を処理
        await page.goto('https://www.deutscher-galopp.de')
        await asyncio.sleep(3)
        
        try:
            await page.waitForSelector('#cookieNoticeDeclineCloser', {'visible': True, 'timeout': 5000})
            await page.click('#cookieNoticeDeclineCloser')
            await asyncio.sleep(3)
        except Exception as e:
            print('cookie notice not found')
        
        for race_id in race_ids:
            await page.goto('https://www.deutscher-galopp.de/gr/renntage/rennen.php?id=' + race_id)
            await asyncio.sleep(3)
            
            # Check if the table with id 'ergebnis' exists
            ergebnis_exists = await page.querySelector('table#ergebnis') is not None
            
            if ergebnis_exists:
                race_exists = await sync_to_async(TodayErgebnis.objects.filter(race_id=race_id).exists)()
                if not race_exists:
                    # Extract number and horse_id from the 'ergebnis' table
                    number_texts = await page.querySelectorAllEval(
                        'table#ergebnis td.dtr-control',
                        'tds => tds.map(td => td.innerText)'
                    )
                    horse_hrefs = await page.querySelectorAllEval(
                        'table#ergebnis a.boxIframeGroup',
                        'anchors => anchors.map(a => a.getAttribute("href").match(/\/gr\/pferd\/(\d+)\//)[1])'
                    )
                    quote_texts = await page.querySelectorAllEval(
                        'table#ergebnis span.quote',
                        'spans => spans.map(span => span.innerText)'
                    )
                    
                    # Save each record to TodayErgebnis model
                    for number, horse_id, quote in zip(number_texts, horse_hrefs, quote_texts[1:]):
                        await sync_to_async(TodayErgebnis.objects.create)(race_id=race_id, platz=number, quote=quote, horse_id=horse_id)

            else:
                # Extract horse_id and quote from the 'nennungen' table
                horse_hrefs = await page.querySelectorAllEval(
                    'table#nennungen a.boxIframeGroup',
                    'anchors => anchors.map(a => a.getAttribute("href").match(/\/gr\/pferd\/(\d+)\//)[1])'
                )
                quote_texts = await page.querySelectorAllEval(
                    'table#nennungen span.quote',
                    'spans => spans.map(span => span.innerText)'
                )
                
                # Save each record to TodayOdds model
                for horse_id, quote in zip(horse_hrefs, quote_texts[1:]):
                    await sync_to_async(TodayOdds.objects.create)(race_id=race_id, quote=quote, horse_id=horse_id)

        await browser.close()


    def handle(self, *args, **options):
        asyncio.run(self.main())