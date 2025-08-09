from flask import Blueprint, request, jsonify
from models import db, User, bcrypt


register_blueprint = Blueprint('register', __name__)

@register_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required.'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email is already registered.'}), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201
