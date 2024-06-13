from django.db import models

# Create your models here.
class HorseResults(models.Model):
    race_horse_id = models.CharField(max_length=30, unique=True)
    date = models.DateField()
    ort = models.CharField(max_length=30)
    title = models.CharField(max_length=100)
    strs = models.IntegerField()
    distanz = models.IntegerField()
    kategorie = models.CharField(max_length=100)
    platz = models.IntegerField()
    gew = models.FloatField(null=True, blank=True)
    gag = models.FloatField(null=True, blank=True)
    evq = models.FloatField(null=True, blank=True)
    preisgeld = models.IntegerField()
    horse_id = models.CharField(max_length=10)
    race_id = models.CharField(max_length=10)

    class Meta:
        verbose_name = "戦績"
        verbose_name_plural = "戦績"
        db_table = 'horseresults'
        

class RaceResults(models.Model):
    race_horse_id = models.CharField(max_length=100, unique=True)
    ort = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    this_race_nr = models.CharField(max_length=100, null=True, blank=True)
    kategorie = models.CharField(max_length=100, null=True, blank=True)
    distanz = models.CharField(max_length=100, null=True, blank=True)
    boden = models.CharField(max_length=100, null=True, blank=True)
    platz = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    race_time = models.CharField(max_length=100, null=True, blank=True)
    abstand_zeit = models.CharField(max_length=10, null=True, blank=True)
    passing_order = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    reiter = models.CharField(max_length=100, null=True, blank=True)
    evq = models.FloatField(null=True, blank=True)
    gew = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=100, null=True, blank=True)
    box = models.CharField(max_length=100, null=True, blank=True)  
    abstand = models.CharField(max_length=100, null=True, blank=True)  
    preisgeld = models.CharField(max_length=100, null=True, blank=True)
    besitzer = models.CharField(max_length=100, null=True, blank=True)
    trainer = models.CharField(max_length=100, null=True, blank=True)
    pay_sieg = models.CharField(max_length=100, null=True, blank=True)  
    hit_sieg = models.FloatField(null=True, blank=True)
    pay_platz = models.CharField(max_length=100, null=True, blank=True)  
    hit_platz = models.FloatField(null=True, blank=True)
    pay_zweier = models.CharField(max_length=100, null=True, blank=True)  
    pay_dreier = models.CharField(max_length=100, null=True, blank=True)  
    sire = models.CharField(max_length=100, null=True, blank=True) 
    damsire = models.CharField(max_length=100, null=True, blank=True) 
    horse_id = models.CharField(max_length=100)
    race_id = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "レース結果"
        verbose_name_plural = "レース結果"
        db_table = 'raceresults'
        

class CombinedResults(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    boden = models.CharField(max_length=100, blank=True, null=True)
    reiter = models.CharField(max_length=100, blank=True, null=True)
    abstand = models.CharField(max_length=100, blank=True, null=True)
    abstand_zeit = models.CharField(max_length=10, null=True, blank=True)
    passing_order = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    race_time = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    box = models.CharField(max_length=100, null=True, blank=True)
    ort = models.CharField(max_length=100, null=True, blank=True)
    this_race_nr = models.CharField(max_length=100, null=True, blank=True)
    ortshort = models.CharField(max_length=100, null=True, blank=True)
    strs = models.IntegerField(blank=True, null=True)
    distanz = models.IntegerField(blank=True, null=True)
    kategorie = models.CharField(max_length=100, null=True, blank=True)
    platz = models.IntegerField(blank=True, null=True)
    gew = models.FloatField(blank=True, null=True)
    gag = models.FloatField(blank=True, null=True)
    evq = models.FloatField(blank=True, null=True)
    horse_id = models.CharField(max_length=255)
    race_id = models.CharField(max_length=255)
    race_horse_id = models.CharField(max_length=255, unique=True)
    
    class Meta:
        verbose_name = "馬柱"
        verbose_name_plural = "馬柱"
        db_table = 'combinedresults'