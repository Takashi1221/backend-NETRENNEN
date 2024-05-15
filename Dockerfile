FROM python:3.12-bullseye

# 作業ディレクトリを設定
WORKDIR .

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    # pyppeteerが依存するLinuxライブラリも取得
    libnss3 \
    libatk1.0-0 \
    libxtst6 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# アプリケーションのコードをコピー
COPY . .

# Pythonの依存関係をインストール
RUN pip install --no-cache-dir -r requirements.lock

# アプリケーションがリッスンするポートを示す
EXPOSE 8000

# アプリケーションの実行
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]