from flask import Blueprint, request, jsonify
from app.models.user import User
from app.utils.jwt import validate_token
from app.utils.database import db
from sqlalchemy.dialects.postgresql import UUID

bp = Blueprint('users', __name__)

@bp.route('/<id>', methods=['GET'])
@validate_token()
def get_user(id):
    user = User.query.get(UUID(id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': str(user.id),
        'email': user.email,
        'name': user.name,
        'profile_picture': user.profile_picture
    })

@bp.route('/<id>', methods=['PUT'])
@validate_token()
def update_user(id):
    from flask_jwt_extended import get_jwt_identity
    if get_jwt_identity() != id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    user = User.query.get(UUID(id))
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.name = data.get('name', user.name)
    user.profile_picture = data.get('profile_picture', user.profile_picture)
    db.session.commit()
    return jsonify({'message': 'Updated'})