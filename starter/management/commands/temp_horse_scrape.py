from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.conf import settings
from django.utils.timezone import make_aware, get_current_timezone
from datetime import datetime
import pandas as pd
import re
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from io import StringIO
import asyncio
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
from asgiref.sync import sync_to_async
from starter.models import Renntermine, Starter, HorseProfi, HorsePedigree
from results.models import HorseResults, RaceResults, CombinedResults
import pickle
import random




class Command(BaseCommand):
    help = 'Scrape horse data and update database'
    
    async def random_sleep(self):
        # 1秒から4秒のランダムな時間を生成
        sleep_time = random.uniform(1, 4)
        await asyncio.sleep(sleep_time)
    

    async def get_horse_ids(self):
        # Pickleファイルからリストを読み込む
        with open('horse_list.pkl', 'rb') as f:
            loaded_list = pickle.load(f)
            
        # まだデータベースに存在しないhorse_idだけを抽出
        existing_ids = await sync_to_async(set)(HorsePedigree.objects.values_list('horse_id', flat=True))
        horse_id_list = [horse_id for horse_id in loaded_list if horse_id not in existing_ids]

        print(len(horse_id_list))
        return horse_id_list


    async def scrape(self, horse_id_list):
        # ブラウザを起動
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 2080})
        
        # ログインするページにアクセス
        await page.goto('https://www.deutscher-galopp.de/')
        await self.random_sleep()
        # ログインモーダルを表示させるボタンをクリック
        await page.click('#blockTopInner > div:nth-child(2)')
        await asyncio.sleep(1) 
        # ログイン情報を入力
        await page.type('input[name="benutzername"]', 'miolla21')
        await page.type('input[name="passwort"]', 'rupan3939')
        login_button_selector = 'div.greenButton.loginActionButton'
        await page.waitForSelector(login_button_selector, {'visible': True})
        await page.click(login_button_selector)
        await page.waitForNavigation({'waitUntil': 'networkidle0'})

        # ログイン後のページに移動するまで待機（適切なセレクタがあればそれをwaitForSelectorに使う）
        profi_dfs = {}
        results_dfs = {}
        pedigree_dfs = {}

        for horse in tqdm(horse_id_list):
            try:
                horse_url = 'https://www.deutscher-galopp.de/gr/pferd/' + horse
                await page.goto(horse_url, {'waitUntil': 'networkidle0'})
                await self.random_sleep()
                page_content = await page.content()
                
                # プロファイル取得
                xpath = '//*[@id="navigationBreadcrumbPageTitle"]'
                elements = await page.xpath(xpath)
                if elements:
                    text = await page.evaluate('(element) => element.textContent', elements[0])
                    name = text.split("(")[0]
                    birth = text.split("(")[1].split(",")[0]

                    table_html = await page.evaluate(
                        '''() => {
                            const table = document.querySelector('.tabelle-profil');
                            return table ? table.outerHTML : null;
                        }'''
                    )
                    if table_html:
                        table_io = StringIO(table_html)
                        df_profi = pd.read_html(table_io)[0]
                        df_profi = df_profi.T
                        df_profi.columns = df_profi.iloc[0] # １行目をカラムに設定
                        df_profi = df_profi.drop(df_profi.index[0])
                        df_profi = df_profi.reset_index(drop=True)
                        df_profi = df_profi[["Geschlecht", "Standort", "Trainer", "Besitzer", "Züchter", "Familie"]]
                        df_profi["Name"] = name
                        df_profi["Birth"] = birth
                        df_profi["horse_id"] = horse
                else:
                    columns = ["Geschlecht", "Standort", "Trainer", "Besitzer", "Züchter", "Familie", "Name", "Birth"]
                    df_profi = pd.DataFrame(columns=columns)
                    df_profi.loc[0] = ['-'] * len(columns)
                    df_profi["horse_id"] = horse
                    
                # 戦績テーブルを取得
                table_html = await page.evaluate(  # TableHTMLを取得
                    '''() => {
                        const table = document.querySelector('#rennleistungen');
                        return table ? table.outerHTML : null;
                    }'''
                )
                if table_html:
                    table_io = StringIO(table_html)
                    df_results = pd.read_html(table_io)[0]  #  DFがリストの1要素目にあるので
                    remove_record = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]
                    df_results = df_results[~df_results["Rennort"].isin(remove_record)]
                    #  メモリの節約とエラー発見の側面からあえてループ内で毎回整形していく(ひとまず)
                    df_results['title'] = df_results['Rennen'].str.split(" - | – ").str[0].str.replace(r"\s+", "", regex=True)
                    df_results['title'] = df_results['title'].str.split("(").str[0].str.replace(r"\s+", "", regex=True)
                    df_results['title'] = df_results['title'].str.replace('Rennvideo', '', regex=False)
                    df_results["platz"] = df_results["Platz"].str.split("/").str[0].str.replace(r"\s+", "", regex=True)
                    df_results["platz"] = pd.to_numeric(df_results['platz'], errors='coerce')
                    df_results["distanz"] = df_results["Distanz"].str.split("m").str[0].str.replace(r"\s+", "", regex=True)
                    df_results['distanz'] = df_results['distanz'].str.replace('.', '', regex=False).astype(int)
                    df_results["strs"] = df_results["Platz"].str.split("/").str[1].str.replace(r"\s+", "", regex=True).astype(int)
                    df_results["gew"] = df_results["Gew."].str.split("kg").str[0].str.replace(r"\s+", "", regex=True)
                    df_results['gew'] = df_results['gew'].str.replace(',', '.', regex=False)
                    df_results["gew"] = pd.to_numeric(df_results['gew'], errors='coerce')
                    if 'GAG' in df_results.columns:  #  GAG列がない場合がある
                        df_results["gag"] = df_results["GAG"].str.split("kg").str[0].str.replace(r"\s+", "", regex=True)
                    else:
                        df_results["gag"] = "-"
                    df_results['gag'] = df_results['gag'].str.replace(',', '.', regex=False)
                    df_results["gag"] = pd.to_numeric(df_results['gag'], errors='coerce')
                    df_results["evq"] = df_results['EVQ'] / 10.0  #  なぜか小数点が消えるので
                    df_results["date"] = pd.to_datetime(df_results['Datum'], format='%d.%m.%Y').dt.date
                    df_results["preisgeld"] = df_results["Preisgeld"].str.split("€").str[0].str.replace(r"\s+", "", regex=True)
                    df_results['preisgeld'] = df_results['preisgeld'].str.replace('.', '', regex=False).astype(int)
                    sum_preisgeld = df_results['preisgeld'].sum()
                    df_results["horse_id"] = horse
                    
                    soup = BeautifulSoup(table_html, 'html.parser')
                    a_tags = soup.select('table#rennleistungen a')
                    id_regex = re.compile(r'id=(\d+)')
                    race_ids = [id_regex.search(a['href']).group(1) for a in a_tags if id_regex.search(a['href'])]
                    df_results["race_id"] = race_ids
                    df_results["race_horse_id"] = df_results["race_id"] + df_results["horse_id"]
                    df_results = df_results.rename(columns={"Rennort":"ort", "Kategorie":"kategorie"})
                    selected_df = df_results[["race_horse_id", "date", "ort", "title", "strs", "distanz", "kategorie", "platz", "gew", "gag", "evq", "preisgeld","horse_id", "race_id"]]
                    selected_df = selected_df.fillna(0)
                    results_dfs[horse] = selected_df
                    df_profi["Total_Earnings"] = sum_preisgeld # 戦績から総獲得賞金を作成
                else:
                    print("テーブルが見つかりませんでした。")
                    df_profi["Total_Earnings"] = 0
                
                # このタイミングでprofi_dfを格納
                df_profi = df_profi.fillna(0)
                df_profi.columns.name = None
                profi_dfs[horse] = df_profi
                    
                # 血統テーブル取得
                pedigree_url = 'https://www.deutscher-galopp.de/gr/pferd/' + horse + '#pedigree'
                await page.goto(pedigree_url, {'waitUntil': 'networkidle0'})
                await asyncio.sleep(1) 
                page_content = await page.content()
                
                soup = BeautifulSoup(page_content, 'html.parser')
                nodes = soup.select('.innerNode')
                pedigree_data = []
                for node in nodes:
                    top = node.select_one('.nodeTop').text.split("(")[0].strip()
                    bottom = node.select_one('.nodeBottom').text.split("(")[0].strip()
                    pedigree_data.append(top)
                    pedigree_data.append(bottom)
                pedigree_df = pd.DataFrame()
                for i, name in enumerate(pedigree_data, start=1):
                    pedigree_df[f'pedigree_{i}'] = [name] # 単一の値をリスト代入
                    
                a_tags = soup.select('.firstNode a') # 母と父に関してはhorse_idも取得
                pedigree_df["sire_id"] = a_tags[0]['href'].split("pferd/")[1]
                pedigree_df["dam_id"] = a_tags[1]['href'].split("pferd/")[1]
                    
                pedigree_df["horse_id"] = horse
                pedigree_dfs[horse] = pedigree_df
                
            # エラー発生、ループから脱出           
            except Exception as e:
                print(f"An error occurred for race ID {race_id}: {e}")
                break  
            
        await browser.close() 
        profi_df = pd.concat(profi_dfs.values()).reset_index(drop=True)
        results_df = pd.concat(results_dfs.values()).reset_index(drop=True)
        pedigree_df = pd.concat(pedigree_dfs.values()).reset_index(drop=True)

        return profi_df, results_df, pedigree_df
        
        
    async def add_horse_to_db(self, profi_df, results_df, pedigree_df):
        # HorseResultsモデルへ同期的にデータ追加
        for _, row in results_df.iterrows():
            try:
                await sync_to_async(HorseResults.objects.get_or_create, thread_sensitive=True)(
                    race_horse_id=row['race_horse_id'],
                    defaults={
                        'date': row['date'],
                        'ort': row['ort'],
                        'title': row['title'],
                        'strs': row['strs'],
                        'distanz': row['distanz'],
                        'kategorie': row['kategorie'],
                        'platz': row['platz'],
                        'gew': row['gew'],
                        'gag': row['gag'],
                        'evq': row['evq'],
                        'preisgeld': row['preisgeld'],
                        'horse_id': row['horse_id'],
                        'race_id': row['race_id'],
                    }
                )
            except IntegrityError:
                # race_horse_idが既に存在する場合、このレコードをスキップ
                pass
            
        # HorseProfiモデルへ同期的にデータ追加
        for _, row in profi_df.iterrows():
            try:
                # update_or_createを使用して条件分岐
                obj, created = await sync_to_async(HorseProfi.objects.update_or_create, thread_sensitive=True)(
                    horse_id=row['horse_id'],
                    # データあれば総獲得賞金のみ更新
                    defaults={
                        'total_earnings': row['Total_Earnings']
                    }
                )
                # レコードが新規作成された場合は他のフィールドも追加
                if created:
                    obj.sex = row['Geschlecht']
                    obj.standort = row['Standort']
                    obj.trainer = row['Trainer']
                    obj.owner = row['Besitzer']
                    obj.breeder = row['Züchter']
                    obj.family = row['Familie']
                    obj.name = row['Name']
                    obj.birth = row['Birth']
                    await sync_to_async(obj.save)()
            except IntegrityError:
                pass

        # HorsePedigreeモデルへ同期的にデータ追加
        for _, row in pedigree_df.iterrows():
            try:
                await sync_to_async(HorsePedigree.objects.get_or_create, thread_sensitive=True)(
                    horse_id=row['horse_id'],
                    defaults=row.to_dict() # DFとモデルのカラム名は完全一致していること
                )
            except IntegrityError:
                pass
            
    

    async def main(self):
        horse_id_list = await self.get_horse_ids()
        profi_df, results_df, pedigree_df = await self.scrape(horse_id_list)
        await self.add_horse_to_db(profi_df, results_df, pedigree_df)
                                       
    
    def handle(self, *args, **options):
        # asyncio.run() で非同期処理を同期的に実行
        asyncio.run(self.main())

