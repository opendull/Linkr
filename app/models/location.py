from app.utils.database import db
from sqlalchemy.dialects.postgresql import UUID

class Location(db.Model):
    __tablename__ = 'locations'
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())