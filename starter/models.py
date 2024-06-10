from django.db import models


class Renntermine(models.Model):
    date = models.DateField(verbose_name="日付")
    location = models.CharField(max_length=20, verbose_name="場所")
    number = models.IntegerField(verbose_name="番号")
    title = models.CharField(max_length=100, verbose_name="レース名")
    start = models.CharField(max_length=10,verbose_name="発走時刻")
    distance = models.CharField(max_length=10,verbose_name="距離")
    categorie = models.CharField(max_length=100,verbose_name="クラス")
    starters = models.IntegerField(verbose_name="頭数")
    race_id = models.CharField(max_length=20, verbose_name="レースID", unique=True, primary_key=True)
    
    class Meta:
        verbose_name = "開催レース一覧"
        verbose_name_plural = "開催レース一覧"
        db_table = 'renntermine'
        
        
class Starter(models.Model):
    number = models.CharField(max_length=5,verbose_name="馬番")
    name = models.CharField(max_length=40, verbose_name="馬名")
    equip = models.CharField(blank=True, null=True, max_length=40, verbose_name="馬具")
    gag = models.CharField(max_length=10,verbose_name="GAG")
    box = models.CharField(max_length=5, verbose_name="枠番")
    alter = models.CharField(max_length=3,verbose_name="馬齢")
    owner = models.CharField(max_length=50,verbose_name="オーナー")
    trainer = models.CharField(max_length=50,verbose_name="トレーナー")
    jocky = models.CharField(max_length=50,verbose_name="ジョッキー")
    gew = models.CharField(max_length=30,verbose_name="斤量")
    erlbnis = models.CharField(blank=True, null=True, max_length=30,verbose_name="減量")
    race_id = models.CharField(max_length=20, verbose_name="レースID")
    horse_id = models.CharField(max_length=20, verbose_name="馬ID")
    
    class Meta:
        verbose_name = "出走馬一覧"
        verbose_name_plural = "出走馬一覧"
        db_table = 'starter'
        
        
class HorseProfi(models.Model):
    sex = models.CharField(max_length=100,verbose_name="性別")
    standort = models.CharField(max_length=100, verbose_name="スタリオン")
    trainer = models.CharField(max_length=100,verbose_name="調教師")
    owner = models.CharField(max_length=100, verbose_name="馬主")
    breeder = models.CharField(max_length=100,verbose_name="生産者")
    family = models.CharField(max_length=50,verbose_name="牝系番号")
    name = models.CharField(max_length=50,verbose_name="馬名")
    birth = models.CharField(max_length=50,verbose_name="生まれ年")
    total_earnings = models.IntegerField(blank=True, null=True, verbose_name="総獲得賞金")
    horse_id = models.CharField(max_length=50, unique=True, verbose_name="馬ID")
    
    class Meta:
        verbose_name = "馬プロフィール"
        verbose_name_plural = "馬プロフィール"
        db_table = 'horseprofi'
        
        
class HorsePedigree(models.Model):
    pedigree_1 = models.CharField(max_length=100,verbose_name="父")
    pedigree_2 = models.CharField(max_length=100,verbose_name="母父")
    pedigree_3 = models.CharField(max_length=100)
    pedigree_4 = models.CharField(max_length=100)
    pedigree_5 = models.CharField(max_length=100,verbose_name="母母父")
    pedigree_6 = models.CharField(max_length=100)
    pedigree_7 = models.CharField(max_length=100)
    pedigree_8 = models.CharField(max_length=100)
    pedigree_9 = models.CharField(max_length=100)
    pedigree_10 = models.CharField(max_length=100)
    pedigree_11 = models.CharField(max_length=100)
    pedigree_12 = models.CharField(max_length=100)
    pedigree_13 = models.CharField(max_length=100)
    pedigree_14 = models.CharField(max_length=100)
    pedigree_15 = models.CharField(max_length=100)
    pedigree_16 = models.CharField(max_length=100)
    pedigree_17 = models.CharField(max_length=100)
    pedigree_18 = models.CharField(max_length=100)
    pedigree_19 = models.CharField(max_length=100)
    pedigree_20 = models.CharField(max_length=100)
    pedigree_21 = models.CharField(max_length=100)
    pedigree_22 = models.CharField(max_length=100)
    pedigree_23 = models.CharField(max_length=100)
    pedigree_24 = models.CharField(max_length=100)
    pedigree_25 = models.CharField(max_length=100)
    pedigree_26 = models.CharField(max_length=100)
    pedigree_27 = models.CharField(max_length=100)
    pedigree_28 = models.CharField(max_length=100)
    pedigree_29 = models.CharField(max_length=100)
    pedigree_30 = models.CharField(max_length=100)
    sire_id = models.CharField(max_length=50)
    dam_id = models.CharField(max_length=50)
    horse_id = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = "現役馬血統"
        verbose_name_plural = "現役馬血統"
        db_table = 'horsepedigree'
        

class KalenderModel(models.Model):
    datum = models.DateField()
    rennort = models.CharField(max_length=50)
    renntitel = models.CharField(max_length=100)
    distanz = models.CharField(max_length=20)
    kategorie = models.CharField(max_length=100)
    stute = models.CharField(max_length=20)
    preisgeld = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = "重賞日程"
        verbose_name_plural = "重賞日程"
        db_table = 'rennkalender'
        

class TodayErgebnis(models.Model):
    race_id = models.CharField(max_length=255)
    platz = models.CharField(max_length=255)
    quote = models.CharField(max_length=255)
    horse_id = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = "当日レース結果"
        verbose_name_plural = "当日レース結果"
        db_table = 'TodayErgebnis'
        
class TodayOdds(models.Model):
    race_id = models.CharField(max_length=255)
    quote = models.CharField(max_length=255)
    horse_id = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = "当日オッズ"
        verbose_name_plural = "当日オッズ"
        db_table = 'TodayOdds'