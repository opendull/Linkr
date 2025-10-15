from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from datetime import datetime, timedelta
from app.utils.database import db
from app.models.token import Token

def generate_token(user_id):
    expires = timedelta(hours=1)
    token = create_access_token(identity=user_id, expires_delta=expires)
    expires_at = datetime.utcnow() + expires
    new_token = Token(user_id=user_id, token=token, expires_at=expires_at)
    db.session.add(new_token)
    db.session.commit()
    return token

def validate_token():
    def decorator(f):
        @jwt_required()
        def wrapper(*args, **kwargs):
            token = get_jwt().get('jti')
            user_id = get_jwt_identity()
            tok = Token.query.filter_by(user_id=user_id, token=token).first()
            if not tok or not tok.is_valid or tok.revoked_at or tok.expires_at < datetime.utcnow():
                return {'error': 'Invalid token'}, 401
            return f(*args, **kwargs)
        return wrapper
    return decorator