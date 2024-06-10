import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
import pandas as pd
import re
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from io import StringIO
import asyncio
from pyppeteer import launch
from asgiref.sync import sync_to_async
from results.models import HorseResults, RaceResults
import random
from decouple import config, Csv


# DEBUG setting
os.environ['DEBUG'] = 'puppeteer:*'
# Load env.
dg_key = config('DG_KEY')
print(dg_key)
# logging setting
logging.basicConfig(level=logging.DEBUG, filename='/tmp/pyppeteer.log', filemode='w')


class Command(BaseCommand):
    help = 'Scrape race results and update database'
    
    async def random_sleep(self):
        # creat random time
        sleep_time = random.uniform(1, 4)
        await asyncio.sleep(sleep_time)
    

    async def get_existing_race_ids(self):
        # Extract only race_ids not in the DB.
        existing_ids = await sync_to_async(set)(RaceResults.objects.values_list('race_id', flat=True))
        
        return existing_ids


    async def scrape(self, existing_ids):
        
        try:
            # Launch the browser
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-software-rasterizer'], dumpio=True)
            page = await browser.newPage()
            await page.setViewport({'width': 1920, 'height': 2080})
            
            # Navigate to the login page
            await page.goto('https://www.deutscher-galopp.de')
            await self.random_sleep()
            
            try:
                # Handle cookie consent if present
                await page.waitForSelector('#cookieNoticeDeclineCloser', {'visible': True, 'timeout': 5000})
                await page.click('#cookieNoticeDeclineCloser')
                await asyncio.sleep(5)
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                
            # Click the button to show the login modal
            try:
                login_button_xpath = '/html/body/div[1]/div/div[4]/div[1]/div/div[1]/div/div[2]'
                await page.waitForXPath(login_button_xpath, {'visible': True, 'timeout': 5000})
                login_button_element = await page.xpath(login_button_xpath)
                if login_button_element:
                    await login_button_element[0].click()
                print('First login button clicked.')
                await page.type('input[name="benutzername"]', 'miolla21')
                await page.type('input[name="passwort"]', dg_key)
                await page.screenshot({'path': 'before_click.png'})
                
                await page.waitForSelector('.greenButton.loginActionButton', {'visible': True, 'timeout': 5000})
                await page.click('.greenButton.loginActionButton')
                await self.random_sleep()
                print('Second login button clicked.')
            except Exception as e:
                print(f"エラーが発生しました: {e}")
            
            # Go to Ergebnisse
            await page.goto('https://www.deutscher-galopp.de/gr/renntage/ergebnisse/')
            # Retrieve all accordion header elements
            accordion_headers = await page.querySelectorAll('.accordionHeader')
            
            # Click each accordion header
            race_ids = [] 
            for header in accordion_headers[:5]:
                await self.random_sleep()
                await header.click()
                # Get elements with the class "accordionContent" that have display: block
                accordion_contents = await page.querySelectorAll('.accordionContent')
                
                for content in accordion_contents[:5]:
                    display = await page.evaluate('(element) => getComputedStyle(element).display', content)
                    if display == 'block':
                        # Get all href attributes within the "#accordionElementOuter" element
                        hrefs = await page.evaluate('''
                            (content) => Array.from(content.querySelectorAll('a')).map(a => a.href)
                        ''', content)
                        
                        for href in hrefs:
                            match = re.search(r'id=(\d+)', href)
                            if match:
                                race_id = match.group(1)
                                    
                            race_ids.append(race_id)

            unique_races = list(set(race_ids))
            race_id_list = [race_id for race_id in unique_races if race_id not in existing_ids]
            
            if race_id_list:
                dfs={}
                for race_id in tqdm(race_id_list):
                    try:
                        horse_url = 'https://www.deutscher-galopp.de/gr/renntage/rennen.php?id=' + race_id
                        await page.goto(horse_url)
                        await self.random_sleep()
                        
                        title_element = await page.xpath('//*[@id="accordionAusschreibung"]/h3/div[1]')
                        title_texts = []
                        if title_element:
                            title_spans = await title_element[0].xpath('.//span')
                            for span in title_spans:
                                title_text = await page.evaluate('(element) => element.textContent', span)
                                title_texts.append(title_text)
                            ort = title_texts[0]
                            title = title_texts[1]
                            input_str = title_texts[2]
                            if "," in input_str:
                                date_str, time_str = input_str.split(", ")
                            else:
                                date_str = input_str
                                time_str = None
                                
                        race_nr_element = await page.xpath('//*[@id="Stammdaten"]/div/div[1]/div[1]/span[2]')
                        if race_nr_element:  # Retrieve this race's number
                            race_nr_text = await page.evaluate('(race_nr_element) => race_nr_element.textContent', race_nr_element[0])
                        
                        for i in range(1, 5):
                            # Retrieve a specific span element
                            span_element = await page.xpath(f'//*[@id="accordionAusschreibung"]/h3/div[2]/span[{i}]')
                            if span_element:
                                text = await page.evaluate('(element) => element.textContent', span_element[0])
                                if i == 1:
                                    kategorie = text
                                elif i == 2:
                                    distanz = text
                                elif i == 4:
                                    boden = text.split(':')[-1].strip()
                            else:
                                if i == 1:
                                    kategorie = "-"
                                elif i == 2:
                                    distanz = "-"
                                elif i == 4:
                                    boden = "-"
                            
                        # creat Dataframe
                        page_content = await page.content()
                        df = pd.DataFrame()
                        table_html = await page.evaluate( 
                            '''() => {
                                const table = document.querySelector('#ergebnis');
                                return table ? table.outerHTML : null;
                            }'''
                        )
                        if table_html:
                            table_io = StringIO(table_html)
                            table_df = pd.read_html(table_io)
                            if table_df:
                                df = table_df[0]
                                other_text = df['Name'].iloc[-1]
                                df = df.drop(df.index[-1])
                                
                                # Create columns for race-time and return-money
                                split_zeit_text = other_text.split("ZEIT DES RENNENS:")
                                if len(split_zeit_text) > 1:
                                    race_time = split_zeit_text[1].split()[0]
                                    df["race_time_origin"] = race_time
                                    
                                    # Convert "race_time_origin" to seconds
                                    def convert_to_seconds(time_str):
                                        minutes, seconds = time_str.split(':')
                                        seconds, fraction = seconds.split(',')
                                        total_seconds = int(minutes) * 60 + int(seconds) + float(f'0.{fraction}')
                                        return total_seconds

                                    df["race_time_second"] = df["race_time_origin"].apply(convert_to_seconds)
                                    
                                    if split_zeit_text[0]:
                                        payout_text = split_zeit_text[0]
                                        siegwette = re.search(r"Siegwette ([\d\.]+,\d+)", payout_text)
                                        platzwette = re.search(r"Platzwette ([\d+,\/\s]+)", payout_text)
                                        zweierwette = re.search(r"Zweierwette ([\d\.]+,\d+)", payout_text)
                                        dreierwette = re.search(r"Dreierwette ([\d\.]+,\d+)", payout_text)
                                        if siegwette:
                                            df["pay_sieg"] = siegwette.group(1)
                                            df['hit_sieg'] = [0.0] * len(df)
                                            df.at[0, "hit_sieg"] = float(siegwette.group(1).replace(",", "."))
                                        if platzwette:
                                            df["pay_platz"] = platzwette.group(1)
                                            split_platz = [x.strip() for x in platzwette.group(1).split('/')]
                                            for i in range(len(df)):
                                                if i < len(split_platz):
                                                    df.loc[i, 'hit_platz'] = float(split_platz[i].replace(",", "."))
                                                else:
                                                    df.loc[i, 'hit_platz'] = 0 
                                        else: 
                                            df["pay_platz"] = "-"
                                            df['hit_platz'] = 0.0
                                        if zweierwette:
                                            df["pay_zweier"] = zweierwette.group(1)
                                        else:
                                            df["pay_zweier"] = "-"
                                        if dreierwette:
                                            df["pay_dreier"] = dreierwette.group(1)
                                        else:
                                            df["pay_dreier"] = "-"
                                    else:
                                        df["pay_sieg"] = "-"
                                        df['hit_sieg'] = 0.0
                                        df["pay_platz"] = "-"
                                        df['hit_platz'] = 0.0
                                        df["pay_zweier"] = "-"
                                        df["pay_dreier"] = "-"
                                else:
                                    df["race_time"] = "-"
                                    df["pay_sieg"] = "-"
                                    df['hit_sieg'] = 0.0
                                    df["pay_platz"] = "-"
                                    df['hit_platz'] = 0.0
                                    df["pay_zweier"] = "-"
                                    df["pay_dreier"] = "-"
                                
                                # Convert margin to a number
                                def fraction_to_decimal(x):
                                    if pd.isnull(x):
                                        return x  # NaN
                                    try:
                                        if ' ' in x:
                                            whole, fraction = x.split(' ')
                                            numerator, denominator = map(int, fraction.split('/'))
                                            return float(whole) + numerator / denominator
                                        elif '/' in x:
                                            numerator, denominator = map(int, x.split('/'))
                                            return numerator / denominator
                                        return x  # Return non-numeric rows or integers as they are
                                    except (ValueError, AttributeError):
                                        return x  # Return unconvertible values as they are
                                    
                                if df["Abstand"].notna().any():
                                    replace_rules = {"kurzer ": "", "Hals": "1/4", "Kopf": "0", "Nase": "0", " Längen": "", " Länge": ""}
                                    df["abstand_rechnung"] = df["Abstand"].replace(replace_rules, regex=True).apply(fraction_to_decimal)
                                    df["abstand_rechnung"] = pd.to_numeric(df["abstand_rechnung"], errors='coerce')*0.2
                                    cumulative_sums = [0] * len(df) 
                                    for i in range(len(df)):
                                        if i == 0:
                                            cumulative_sums[i] = df.loc[i, "abstand_rechnung"] if pd.notna(df.loc[i, "abstand_rechnung"]) else 0
                                        else:
                                            if pd.notna(df.loc[i, "abstand_rechnung"]):
                                                cumulative_sums[i] = cumulative_sums[i-1] + df.loc[i, "abstand_rechnung"]
                                            else:
                                                cumulative_sums[i] = cumulative_sums[i-1]
                                    df["abstand_zeit"] = cumulative_sums
                                    df["abstand_zeit"] = df["abstand_zeit"].round(1)
                                    df.at[0, "abstand_zeit"] = -df.loc[1, "abstand_zeit"]
                                    
                                    # Race-time may be missing
                                    try:
                                        df["race_time_second_added"] = df["race_time_second"] + df["abstand_zeit"]
                                        # Overwrite the record for 1st place
                                        df.loc[0, "race_time_second_added"] = df.loc[0, "race_time_second"] + 0
                                        
                                        def seconds_to_german_time_format(total_seconds):
                                            minutes = int(total_seconds // 60)
                                            remaining_seconds = total_seconds % 60
                                            seconds = int(remaining_seconds)
                                            fraction = remaining_seconds - seconds
                                            # Create a string in German time format
                                            fraction_str = f"{fraction:.2f}".split('.')[1]
                                            german_time_format = f"{minutes}:{seconds:02},{fraction_str}"
                                            return german_time_format
                                        
                                        df["race_time"] = df["race_time_second_added"].apply(seconds_to_german_time_format)
                                        
                                    except:
                                        df["race_time"] = "-:--,--"
                                        
                                    df['abstand_zeit'] = df['abstand_zeit'].apply(lambda x: f"{x:.1f}")
                                    
                                else:
                                    # if the "Abstand" column is entirely empty
                                    df["abstand_zeit"] = "-.-"
                                    df["race_time"] = "-:--,--"
                                    
                                df["abstand_zeit"] = df["abstand_zeit"].astype(str).fillna("-.-")
                                
                                # Get horse_id
                                soup = BeautifulSoup(table_html, 'html.parser')
                                a_tags = soup.select('table#ergebnis a')
                                id_regex = re.compile(r'/pferd/(\d+)/')
                                horse_ids = [id_regex.search(a['href']).group(1) for a in a_tags if id_regex.search(a['href'])]
                                df["horse_id"] = horse_ids
                                df["race_id"] = race_id
                                df["race_horse_id"] = df["race_id"] + df["horse_id"]
                                
                                # Prepare other necessary columns
                                df["platz"] = df["Pl."].str.replace('.', '', regex=False)
                                df["gew"] = df["Gew."].str.replace('kg', '', regex=False)
                                try:
                                    df["evq"] = df["Quote"].astype(int) / 10
                                except:
                                    df["evq"] = None
                                df["evq"] = df["evq"].astype(float).fillna(0)
                                    
                                df["ort"] = ort
                                df["title"] = title
                                df['date'] = pd.to_datetime(date_str, format='%d.%m.%Y')
                                try:
                                    time_temp = pd.to_datetime(time_str, format='%H:%M')
                                    df['time'] = time_temp.time()
                                except:
                                    df['time'] = None
                                try:
                                    df['this_race_nr'] = race_nr_text
                                except:
                                    df['this_race_nr'] = "_"
                                    
                                df["kategorie"] = kategorie
                                df["distanz"] = distanz
                                df["boden"] = boden

                                df = df.rename(columns={"Name":"name", "Nr.":"number", "Abstand":"abstand", "Box":"box", "Gewinn":"preisgeld", "Besitzer":"besitzer", "Trainer":"trainer", "Reiter":"reiter"})
                                selected_df = df[['race_horse_id', "ort", "title", "date", "time", "this_race_nr", "kategorie", "distanz", "boden", 'platz', 'name', 'race_time', 'abstand_zeit', 'reiter', 'evq', 'gew', 'number', 'box', 'abstand', 'preisgeld', 'besitzer','trainer',
                                                'pay_sieg','hit_sieg', 'pay_platz', 'hit_platz', 'pay_zweier', 'pay_dreier', 'horse_id', 'race_id']]
                                dfs[race_id] = selected_df
                                await asyncio.sleep(1)
                                
                            else:
                                pass
                        else:
                                pass
                    
                    # Error occurs, exit the loop           
                    except Exception as e:
                        print(f"An error occurred for race ID {race_id}: {e}")
                        break  
                            
                results_df = pd.concat(dfs.values(), ignore_index=True)
                results_df.to_pickle("results_df.pkl")
                
            else:
                results_df = pd.DataFrame()
                
            await page.close()
            await browser.close()
            logging.info('Pyppeteer task completed successfully')
            
        except Exception as e:
            logging.error(f'Error during Pyppeteer task: {e}')  
            raise
        
        return results_df
        
    async def add_results_to_db(self, results_df):
            for _, row in results_df.iterrows():
                try:
                    # Execute synchronous database operations asynchronously
                    await sync_to_async(RaceResults.objects.get_or_create, thread_sensitive=True)(
                        race_horse_id=row['race_horse_id'],
                        defaults={
                            'ort': row['ort'],
                            'title': row['title'],
                            'date': row['date'],
                            'time': row['time'],
                            'this_race_nr': row['this_race_nr'],
                            'kategorie': row['kategorie'],
                            'distanz': row['distanz'],
                            'boden': row['boden'],
                            'platz': row['platz'],
                            'name': row['name'],
                            'race_time': row['race_time'],
                            'abstand_zeit': row['abstand_zeit'],
                            'reiter': row['reiter'],
                            'evq': row['evq'],
                            'gew': row['gew'],
                            'number': row['number'],
                            'box': row['box'],
                            'abstand': row['abstand'],
                            'preisgeld': row['preisgeld'],
                            'besitzer': row['besitzer'],
                            'trainer': row['trainer'],
                            'pay_sieg': row['pay_sieg'],
                            'hit_sieg': row['hit_sieg'],
                            'pay_platz': row['pay_platz'],
                            'hit_platz': row['hit_platz'],
                            'pay_zweier': row['pay_zweier'],
                            'pay_dreier': row['pay_dreier'],
                            'horse_id': row['horse_id'],
                            'race_id': row['race_id'],
                        }
                    )
                except IntegrityError:
                    # if race_horse_id is already exist, skip the record
                    pass


    async def main(self):
        
        existing_ids = await self.get_existing_race_ids()
        results_df = await self.scrape(existing_ids)
        await self.add_results_to_db(results_df)
        
        
    # Execute synchronous operations asynchronously
    def handle(self, *args, **options):
        
        asyncio.run(self.main())