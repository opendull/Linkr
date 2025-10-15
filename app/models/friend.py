from app.utils.database import db
from sqlalchemy.dialects.postgresql import UUID

class Friend(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())