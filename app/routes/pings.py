from flask import Blueprint, request, jsonify
from app.models.ping import Ping
from app.models.user import User
from app.utils.jwt import validate_token
from app.utils.database import db
from sqlalchemy.dialects.postgresql import UUID

bp = Blueprint('pings', __name__)


@bp.route('', methods=['POST'])
@validate_token()
def send_ping():
    from flask_jwt_extended import get_jwt_identity
    data = request.json
    current_id = UUID(get_jwt_identity())
    receiver = User.query.get(UUID(data['receiver_id']))
    if not receiver:
        return jsonify({'error': 'User not found'}), 404
    ping = Ping(sender_id=current_id, receiver_id=receiver.id)
    db.session.add(ping)
    db.session.commit()
    return jsonify({'message': 'Ping sent'})


@bp.route('/incoming', methods=['GET'])
@validate_token()
def get_incoming_pings():
    from flask_jwt_extended import get_jwt_identity
    current_id = UUID(get_jwt_identity())
    pings = Ping.query.filter_by(receiver_id=current_id, status='pending').all()
    return jsonify([{'id': p.id, 'sender_id': str(p.sender_id)} for p in pings])


@bp.route('/<id>/respond', methods=['POST'])
@validate_token()
def respond_ping(id):
    from flask_jwt_extended import get_jwt_identity
    data = request.json
    current_id = UUID(get_jwt_identity())
    ping = Ping.query.filter_by(id=id, receiver_id=current_id).first()
    if not ping or ping.status != 'pending':
        return jsonify({'error': 'Invalid ping'}), 400
    ping.status = data['status']  # 'accepted' or 'rejected'
    ping.updated_at = db.func.now()
    db.session.commit()
    return jsonify({'message': 'Responded'})
