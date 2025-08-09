from flask import Flask, request, jsonify,Blueprint
import pickle
from peds_scraper import Peds  # Pedsクラスを利用

from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8081", "http://127.0.0.1:8081", "http://172.19.0.3:8001"]}})


horse_pedigree_api_blueprint = Blueprint('horse_pedigree_api', __name__)

# 馬名とhorse_idをロード
def load_horse_data(pickle_file):
    with open(pickle_file, 'rb') as f:
        return pickle.load(f)

# グローバルでデータをロード
horse_data_file = "horse_names_and_ids.pkl"
horse_data = load_horse_data(horse_data_file)

@horse_pedigree_api_blueprint.route('/get_pedigree', methods=['POST'])
def get_pedigree():
    try:
        data = request.json
        horse_name = data.get("horse_name")

        if not horse_name:
            return jsonify({"error": "馬名が指定されていません"}), 400

        # 馬名からhorse_idを取得
        horse_id = horse_data.get(horse_name)

        if not horse_id:
            return jsonify({"error": f"馬名 {horse_name} に該当するhorse_idが見つかりませんでした"}), 404

        # 血統データをスクレイピング
        pedigree_data = Peds.scrape([horse_id])

        if pedigree_data.empty:
            return jsonify({"error": f"horse_id {horse_id} に該当する血統データが見つかりませんでした"}), 404

        # 血統データをJSON形式で返す
        return jsonify(pedigree_data.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": f"サーバーエラー: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
