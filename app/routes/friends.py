from flask import Blueprint, request, jsonify
from app.models.friend_request import FriendRequest
from app.models.friend import Friend
from app.models.user import User
from app.utils.jwt import validate_token
from app.utils.database import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import and_, or_

bp = Blueprint('friends', __name__)


@bp.route('', methods=['GET'])
@validate_token()
def get_friends():
    from flask_jwt_extended import get_jwt_identity
    current_id = UUID(get_jwt_identity())
    friends = db.session.query(User).join(Friend).filter(
        or_(Friend.user1_id == current_id, Friend.user2_id == current_id)
    ).all()
    return jsonify([{'id': str(u.id), 'name': u.name} for u in friends])


@bp.route('/request', methods=['POST'])
@validate_token()
def send_request():
    from flask_jwt_extended import get_jwt_identity
    data = request.json
    current_id = UUID(get_jwt_identity())
    receiver = User.query.get(UUID(data['receiver_id']))
    if not receiver:
        return jsonify({'error': 'User not found'}), 404
    if FriendRequest.query.filter_by(requester_id=current_id, receiver_id=receiver.id).first():
        return jsonify({'error': 'Request exists'}), 400
    req = FriendRequest(requester_id=current_id, receiver_id=receiver.id)
    db.session.add(req)
    db.session.commit()
    return jsonify({'message': 'Request sent'})


@bp.route('/request/<id>/accept', methods=['POST'])
@validate_token()
def accept_request(id):
    from flask_jwt_extended import get_jwt_identity
    current_id = UUID(get_jwt_identity())
    req = FriendRequest.query.filter_by(id=id, receiver_id=current_id).first()
    if not req or req.status != 'pending':
        return jsonify({'error': 'Invalid request'}), 400
    req.status = 'accepted'
    req.updated_at = db.func.now()
    u1, u2 = sorted([req.requester_id, req.receiver_id])
    friend = Friend(user1_id=u1, user2_id=u2)
    db.session.add(friend)
    db.session.commit()
    return jsonify({'message': 'Accepted'})


@bp.route('/request/<id>/reject', methods=['POST'])
@validate_token()
def reject_request(id):
    from flask_jwt_extended import get_jwt_identity
    current_id = UUID(get_jwt_identity())
    req = FriendRequest.query.filter_by(id=id, receiver_id=current_id).first()
    if not req or req.status != 'pending':
        return jsonify({'error': 'Invalid request'}), 400
    req.status = 'rejected'
    req.updated_at = db.func.now()
    db.session.commit()
    return jsonify({'message': 'Rejected'})


@bp.route('/<id>', methods=['DELETE'])
@validate_token()
def remove_friend(id):
    from flask_jwt_extended import get_jwt_identity
    current_id = UUID(get_jwt_identity())
    friend = Friend.query.filter(
        or_(
            and_(Friend.user1_id == current_id, Friend.user2_id == UUID(id)),
            and_(Friend.user1_id == UUID(id), Friend.user2_id == current_id)
        )
    ).first()
    if not friend:
        return jsonify({'error': 'Not friends'}), 400
    db.session.delete(friend)
    db.session.commit()
    return jsonify({'message': 'Removed'})
