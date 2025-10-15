from app.utils.database import db
from datetime import datetime

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.Text, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
    issued_at = db.Column(db.DateTime, default=db.func.now())
    expires_at = db.Column(db.DateTime)
    revoked_at = db.Column(db.DateTime)