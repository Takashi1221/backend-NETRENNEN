from .base import *
from decouple import config, Csv
import dj_database_url


# 環境変数の読み込み
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost', cast=Csv())


SENDGRID_API_KEY = config('SENDGRID_API_KEY')


# 環境変数からデータベースURLを取得
DATABASE_URL = config('DATABASE_URL')


# DATABASES設定を作成
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}