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
import logging
from io import StringIO
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch
from asgiref.sync import sync_to_async
from starter.models import Renntermine, Starter, HorseProfi, HorsePedigree
from results.models import HorseResults, RaceResults, CombinedResults



class Command(BaseCommand):
    help = 'Scrape race information and set database'
    
    async def wait_randomly(self, min_seconds, max_seconds):
        """指定された範囲内でランダムに非同期に待機する"""
        wait_time = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(wait_time)

    async def renntermine(self):
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})
        await page.goto('https://www.deutscher-galopp.de')
        await self.wait_randomly(1, 5)
        
        first_elements = await page.xpath('//*[@id="container_1b55c231329b2be55f0183af795f3e19_1"]/div[2]/a')  # MehrAnzeigenボタン
        if first_elements:
            await first_elements[0].click()
            await page.waitForNavigation()  # ページ遷移を待つ
        
        second_elements = await page.xpath('//*[@id="suchergebnis"]/div[2]/div[2]')  # TableViewボタン
        if second_elements:
            await second_elements[0].click()
            table_html = await page.evaluate(  # 直近開催日のTableHTMLを取得
                '''() => {
                    const table = document.querySelector('#racesTable');
                    return table ? table.outerHTML : null;
                }'''
            )
            links = await page.evaluate(  # 'zum Rennen'のURLを取得
                '''() => {
                    const links = Array.from(document.querySelectorAll('#racesTable a.tooltip'));
                    return links.map(link => link.href);
                }'''
            )
        await browser.close()
        
        def extract_id_from_url(row): # race_idを取得
            url = row['link']
            match = re.search(r"id=(\d{7})", url)
            if match:
                return match.group(1)
            else:
                return "not found"
        
        df = pd.DataFrame() # 開催レース情報を格納
        if table_html:
            table_io = StringIO(table_html)
            dfs = pd.read_html(table_io)
            if dfs:
                df = dfs[0] 
                df['Datum'] = pd.to_datetime(df['Datum'], format="%d.%m.%y")
                df['link'] = links
                df['raceid'] = df.apply(extract_id_from_url, axis=1)
                df = df.drop(columns=["Status", "Unnamed: 10"])
                df = df.rename(columns={"Datum":"date", "RNr.":"number", "Rennort":"ort", "Renntitel":"title", "Start":"start",
                                        "Distanz":"distance", "Kategorie":"kategorie", "Preisgeld":"preise", "Starter":"starter"})
            else:
                print("テーブルが見つかりませんでした。") # 基本的にこのテーブルはあります

        return df
        

    async def starter(self, urls, raceids):
        starter_dfs = {}
        for url, raceid in zip(urls, raceids):
            try:
                browser = await launch(headless=True)
                page = await browser.newPage()
                await page.setViewport({'width': 1920, 'height': 1080})
                await page.goto(url)
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
                logger.error(f"エラーが発生しました: {e}")
                raise  # この例外を再発生させることで処理を中断
        starter_df = pd.concat(starter_dfs.values()).reset_index(drop=True)
        return starter_df

    async def fetch_horse_already_have(self):
        # 既に血統データのあるhorse_idをリストとして取得
        horse_already_have = await sync_to_async(list)(HorsePedigree.objects.values_list('horse_id', flat=True))
        return horse_already_have
    


    async def scrape_horse(self, horse_id_list, horse_already_have):
        # ブラウザを起動
        browser = await launch(headless=True, dumpio=True) 
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})
        
        # ログインするページにアクセス
        await page.goto('https://www.deutscher-galopp.de/')
        await self.wait_randomly(1, 5)
        # ログインモーダルを表示させるボタンをクリック
        await page.click('#blockTopInner > div:nth-child(2)')
        await self.wait_randomly(1, 3)
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
        if horse_id_list:
            for horse in tqdm(horse_id_list):
                horse_url = 'https://www.deutscher-galopp.de/gr/pferd/' + horse
                await page.goto(horse_url, {'waitUntil': 'networkidle0'})
                await self.wait_randomly(1, 5)
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
                if horse in horse_already_have:
                    pass
                else:
                    pedigree_url = 'https://www.deutscher-galopp.de/gr/pferd/' + horse + '#pedigree'
                    await page.goto(pedigree_url, {'waitUntil': 'networkidle0'})
                    await self.wait_randomly(1, 5)
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
                

            await browser.close()
            profi_df = pd.concat(profi_dfs.values()).reset_index(drop=True)
            results_df = pd.concat(results_dfs.values()).reset_index(drop=True)
            pedigree_df = pd.concat(pedigree_dfs.values()).reset_index(drop=True)
        else:
            print("リストが空です")
    
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
            
            
            
    async def fetch_horse_results_data(self):
        # HorseResultsモデルからデータを非同期で取得
        horse_results_data = await sync_to_async(list)(HorseResults.objects.values(
            'race_horse_id', 'date', 'ort', 'strs', 'distanz', 'kategorie', 'platz', 'gew', 'gag', 'evq', 'horse_id', 'race_id'
        ))
        return horse_results_data

    async def fetch_race_results_data(self):
        # RaceResultsモデルからデータを非同期で取得
        race_results_data = await sync_to_async(list)(RaceResults.objects.values(
            'race_horse_id', 'title', 'this_race_nr', 'boden', 'reiter', 'abstand', 'abstand_zeit', 'race_time', 'box'
        ))
        return race_results_data
            
    async def combine_data(self):
        # 非同期でデータ取得
        horse_results_data = await self.fetch_horse_results_data()
        race_results_data = await self.fetch_race_results_data()
        # DataFrameに変換
        df_horse = pd.DataFrame(horse_results_data)
        df_race = pd.DataFrame(race_results_data)
        # race_horse_idをキーにして結合
        df_combined = pd.merge(df_horse, df_race, on='race_horse_id', how='left')

        # 欠損値あるとMySQLがエラー起こすので前処理
        df_combined = df_combined.where(pd.notnull(df_combined), None)
        df_combined["abstand_zeit"] = df_combined["abstand_zeit"].astype(float).fillna(1000)

        return df_combined
    
    async def add_combined_to_db(self, df_combined):
        await sync_to_async(CombinedResults.objects.all().delete)()
        for _, row in df_combined.iterrows():
            await sync_to_async(CombinedResults.objects.create, thread_sensitive=True)(
            title=row['title'],
            boden=row['boden'],
            reiter=row['reiter'],
            abstand=row.get('abstand', None),
            abstand_zeit=row.get('abstand_zeit', None),
            race_time=row.get('race_time', None),
            date=row['date'],
            box=row.get('box', None),
            ort=row['ort'],
            this_race_nr=row['this_race_nr'],
            strs=row.get('strs', None),
            distanz=row.get('distanz', None),
            kategorie=row['kategorie'],
            platz=row.get('platz', None),
            gew=row.get('gew', None),
            gag=row.get('gag', None),
            evq=row.get('evq', None),
            horse_id=row['horse_id'],
            race_id=row['race_id'],
            race_horse_id=row['race_horse_id']
            )
    

    async def main(self):
        df_renntermine = await self.renntermine()
        # 初期化してからレース一覧を追加
        await sync_to_async(Renntermine.objects.all().delete)()
        for _, row in df_renntermine.iterrows():
            await sync_to_async(Renntermine.objects.create, thread_sensitive=True)(
            date=row['date'],
            location=row['ort'],
            number=row['number'],
            title=row['title'],
            start=row['start'],
            distance=row['distance'],
            categorie=row['kategorie'],
            starters=row['starter'],
            race_id=row['raceid']
            )
        
        urls = df_renntermine["link"].tolist()
        raceids = df_renntermine["raceid"].tolist()
        starter_df = await self.starter(urls, raceids)

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
            
        horse_id_list = list(set(starter_df['horse_id'].tolist()))  # 重複を排除
        horse_already_have = await self.fetch_horse_already_have()
        profi_df, results_df, pedigree_df = await self.scrape_horse(horse_id_list, horse_already_have)
        await self.add_horse_to_db(profi_df, results_df, pedigree_df)
        
        df_combined = await self.combine_data()
        await self.add_combined_to_db(df_combined)
                                       
    
    def handle(self, *args, **options):
        # asyncio.run() で非同期処理を同期的に実行
        asyncio.run(self.main())

 
    
    
'''
上記のコードは、pyppeteerを使用しているスクリプトでRuntimeError: Event loop is closedというエラーが発生しないようにするための提案です。
この方法は、イベントループの扱いを改善し、pyppeteerとの互換性を高めることを目的としています。
asyncio.get_event_loop()を使用して既存のイベントループを取得する
この方法では、asyncio.run()の代わりにasyncio.get_event_loop()を使用して既存のイベントループを取得し、
run_until_complete()メソッドを使ってメインの非同期関数を実行します。この方法は、イベントループの管理をより明示的に行い、エラーを回過するのに役立ちます。
'''