from flask import Blueprint, request, jsonify
from app.models.location import Location
from app.models.friend import Friend
from app.models.user import User
from app.utils.jwt import validate_token
from app.utils.database import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import and_, or_

bp = Blueprint('locations', __name__)


@bp.route('', methods=['POST'])
@validate_token()
def update_location():
    from flask_jwt_extended import get_jwt_identity
    data = request.json
    user_id = UUID(get_jwt_identity())
    loc = Location.query.get(user_id)
    if loc:
        loc.latitude = data['latitude']
        loc.longitude = data['longitude']
    else:
        loc = Location(user_id=user_id, latitude=data['latitude'], longitude=data['longitude'])
        db.session.add(loc)
    db.session.commit()
    return jsonify({'message': 'Updated'})


@bp.route('/friends', methods=['GET'])
@validate_token()
def get_friends_locations():
    from flask_jwt_extended import get_jwt_identity
    current_id = UUID(get_jwt_identity())
    friends_locs = db.session.query(Location, User).join(Friend).join(User).filter(
        or_(Friend.user1_id == current_id, Friend.user2_id == current_id)
    ).all()
    return jsonify([{
        'user_id': str(u.id),
        'name': u.name,
        'latitude': loc.latitude,
        'longitude': loc.longitude
    } for loc, u in friends_locs])


@bp.route('/<userId>', methods=['GET'])
@validate_token()
def get_location(userId):
    from flask_jwt_extended import get_jwt_identity
    current_id = UUID(get_jwt_identity())
    # Simple check if friends
    if not Friend.query.filter(
        or_(
            and_(Friend.user1_id == current_id, Friend.user2_id == UUID(userId)),
            and_(Friend.user1_id == UUID(userId), Friend.user2_id == current_id)
        )
    ).first():
        return jsonify({'error': 'Not friends'}), 403
    loc = Location.query.get(UUID(userId))
    if not loc:
        return jsonify({'error': 'No location'}), 404
    return jsonify({
        'latitude': loc.latitude,
        'longitude': loc.longitude
    })
