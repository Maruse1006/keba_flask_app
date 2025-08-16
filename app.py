from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

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

load_dotenv()

def create_app():
    app = Flask(__name__)

    # ── CORS（本番ドメインだけ許可） ───────────────────────────
    ALLOWED_ORIGINS = [
        "https://horse-racing-react.vercel.app",  # フロント(Vercel)
        "https://keiba-app.com",                  # Expo/外部クライアント
        "http://localhost:3000",                  # 開発用（必要なら）
        "http://localhost:5173",                  # 開発用（Viteなど）
    ]
    CORS(app, resources={
        r"/api/*": {
            "origins": ALLOWED_ORIGINS,
            # Cookieを使わないなら supports_credentials は不要（Falseのまま）
            "allow_headers": ["Authorization", "Content-Type"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }
    })

    # ── 設定 ────────────────────────────────────────────────
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    # ── ライブラリ初期化 ─────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    Migrate(app, db)

    # ── Blueprint登録 ───────────────────────────────────────
    app.register_blueprint(register_blueprint, url_prefix='/api')
    app.register_blueprint(login_blueprint, url_prefix='/api')
    app.register_blueprint(get_horses_blueprint, url_prefix='/api')
    app.register_blueprint(check_payout_blueprint, url_prefix='/api')
    app.register_blueprint(get_daily_profit_blueprint, url_prefix='/api')
    app.register_blueprint(horse_pedigree_api_blueprint, url_prefix='/api')
    app.register_blueprint(bet_api_blueprint, url_prefix='/api')

    # ── ヘルスチェック ──────────────────────────────────────
    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # ── JWTエラーハンドラ ───────────────────────────────────
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def _unauth(err_str):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    @jwt.invalid_token_loader
    def _invalid(err_str):
        return jsonify({"error": "Invalid token"}), 422

    @jwt.expired_token_loader
    def _expired(jwt_header, jwt_payload):
        return jsonify({"error": "Token expired"}), 401

    return app

# 開発用（python app.py で動かす時だけ）
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
