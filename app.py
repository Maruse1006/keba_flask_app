from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate  # ← 追加！

from models import db, bcrypt
from register import register_blueprint
from login import login_blueprint
from get_horse import get_horses_blueprint
from payout import check_payout_blueprint
from get_daily_profit import get_daily_profit_blueprint
from horse_pedigree_api import horse_pedigree_api_blueprint
from bet import bet_api_blueprint

import os
from dotenv import load_dotenv

# .env を読み込む
load_dotenv()

app = Flask(__name__)
CORS(app)

# 環境変数から設定を読み込む
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# ライブラリの初期化
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)  # ← 追加！

# JWTエラーハンドラ
@jwt.unauthorized_loader
def custom_unauthorized_response(err_str):
    print(f"[JWT ERROR] Missing or invalid auth header: {err_str}")
    return jsonify({"error": "Missing or invalid Authorization header"}), 401

@jwt.invalid_token_loader
def custom_invalid_token_response(err_str):
    print(f"[JWT ERROR] Invalid token: {err_str}")
    return jsonify({"error": "Invalid token"}), 422

@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    print(f"[JWT ERROR] Token expired")
    return jsonify({"error": "Token expired"}), 401

# Blueprint登録
app.register_blueprint(register_blueprint, url_prefix='/api')
app.register_blueprint(login_blueprint, url_prefix='/api')
app.register_blueprint(get_horses_blueprint, url_prefix='/api')
app.register_blueprint(check_payout_blueprint, url_prefix='/api')
app.register_blueprint(get_daily_profit_blueprint, url_prefix='/api')
app.register_blueprint(horse_pedigree_api_blueprint, url_prefix='/api')
app.register_blueprint(bet_api_blueprint, url_prefix='/api')

# 開発環境用サーバー起動
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
