from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Bets(db.Model):
    __tablename__ = 'bets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    profit_or_loss = db.Column(db.Float, default=0.0) 
    comment = db.Column(db.Text, nullable=True)
    date_info = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(10), nullable=False)
    race_number = db.Column(db.Integer, nullable=False)
    round = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
