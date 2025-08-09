FROM python:3.10.14
RUN apt-get update && \
    apt-get -y install mariadb-client

RUN mkdir /code
WORKDIR /code

# 依存関係ファイルを最初にコピー（キャッシュ効率を向上）
COPY requirements.txt /code/

# 依存関係をインストール
RUN pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . /code

# Flaskアプリケーションを指定
ENV FLASK_APP=horse_pedigree_api.py

# Flaskアプリケーションを起動
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
