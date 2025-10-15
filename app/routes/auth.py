from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.token import Token
from app.utils.jwt import generate_token
from app.utils.database import db
from app.utils.jwt import validate_token
import bcrypt

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing fields'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email exists'}), 400
    hash_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    user = User(email=data['email'], password_hash=hash_pw, name=data.get('name', ''))
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registered', 'user_id': str(user.id)}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = generate_token(str(user.id))
    return jsonify({'token': token, 'user_id': str(user.id)})


@bp.route('/logout', methods=['POST'])
@validate_token()
def logout():
    from flask_jwt_extended import get_jwt
    token = get_jwt()['jti']  # Assuming jti is token for simplicity
    tok = Token.query.filter_by(token=token).first()
    if tok:
        tok.is_valid = False
        tok.revoked_at = db.func.now()
        db.session.commit()
    return jsonify({'message': 'Logged out'})
