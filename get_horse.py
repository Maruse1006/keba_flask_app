from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup

# Blueprintの定義
get_horses_blueprint = Blueprint('get_horses', __name__)

@get_horses_blueprint.route('/get_horses', methods=['POST'])
def get_horses():
    try:
        # POSTリクエストからパラメータを取得
        data = request.json
        year = data.get('year')
        day_count = data.get('dayCount')
        place = data.get('place')
        race = data.get('race')
        round_number = data.get('round')

        # URLを作成
        day_count_str = f"{int(''.join(filter(str.isdigit, day_count))):02}"
        place_str = f"{int(place):02}"
        race_str = f"{int(race):02}"
        round_str = f"{int(''.join(filter(str.isdigit, round_number))):02}"
        url = f"https://db.netkeiba.com/race/{year}{place_str}{round_str}{day_count_str}{race_str}/"
        print(f"Scraping URL: {url}")  # デバッグ用

        # HTTPリクエスト
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Referer": "https://db.netkeiba.com/"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return jsonify({"success": False, "error": f"Failed to fetch data. Status code: {response.status_code}"}), 500

        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr')[1:]  # 1行目（ヘッダー）をスキップ

        # 馬番号と馬名を取得
        horses = []
        for row in rows:
            try:
                cols = row.find_all('td')
                if len(cols) >= 4:  # 必要なカラムがあるか確認
                    horse_number = cols[2].text.strip()  # 3つ目のtdから馬番号を取得
                    horse_name_tag = cols[3].find('a')  # 4つ目のtdに馬名がある
                    horse_name = horse_name_tag.text.strip() if horse_name_tag else "不明"
                    horses.append({"number": horse_number, "name": horse_name})
                else:
                    print(f"Skipping incomplete row: {row}")
            except Exception as e:
                print(f"Error processing row: {e}")

        # データを返す
        return jsonify({"success": True, "horses": horses})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
