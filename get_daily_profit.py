from flask import Blueprint, jsonify
from sqlalchemy import func
from models import db, Bets

# Blueprintのインスタンス化
get_daily_profit_blueprint = Blueprint('get_daily_profit', __name__)

@get_daily_profit_blueprint.route('/get_daily_profit_data', methods=['GET'])
def get_daily_profit_data():
    try:
        # 日ごとの収支を計算
        results = db.session.query(
            func.date_format(Bets.date_info, "%Y-%m-%d").label("date"),  # 日付
            func.sum(Bets.amount).label("profit")  # 合計収支
        ).group_by(func.date_format(Bets.date_info, "%Y-%m-%d")).all()

        data = [{"date": result[0], "profit": float(result[1])} for result in results]
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
