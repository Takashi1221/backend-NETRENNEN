from django.db import models

class Article(models.Model):
    date = models.DateField(verbose_name="日付")
    title = models.CharField(max_length=255, verbose_name="タイトル")
    description = models.TextField(verbose_name="概要")
    content = models.TextField(verbose_name="本文")
    image_url = models.CharField(max_length=255, verbose_name="画像URL")
    is_large = models.BooleanField(default=False, verbose_name="大記事")
    gernre = models.CharField(max_length=255, verbose_name="ジャンル")
    
    class Meta:
        verbose_name = "ニュース記事"
        verbose_name_plural = "ニュース記事"
        db_table = 'article'