from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models import db, Bets

bet_api_blueprint = Blueprint('bet_api', __name__)

@bet_api_blueprint.route("/bet-summary", methods=["GET"])
@jwt_required()
def get_bet_summary():
    user_id = int(get_jwt_identity())
    print(f"✅ get_bet_summary: user_id = {user_id}")

    results = db.session.query(
        Bets.date_info,
        Bets.location,
        Bets.round,
        func.sum(Bets.profit_or_loss).label('total_amount')
    ).filter(Bets.user_id == user_id
    ).group_by(
        Bets.date_info,
        Bets.location,
        Bets.round
    ).all()

    daily = [{
        "date_info": r[0],
        "location": r[1],
        "round": r[2],
        "total_amount": float(r[3]) if r[3] is not None else 0.0
    } for r in results]

    total = db.session.query(func.sum(Bets.profit_or_loss)).filter(Bets.user_id == user_id).scalar()
    total = float(total) if total else 0.0

    return jsonify({
        "total_sum": total,
        "daily": daily
    })
