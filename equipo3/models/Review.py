from datetime import datetime
from models.db import db

class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    idAccommodation = db.Column(db.Integer, db.ForeignKey('accommodation.id', ondelete='CASCADE'), nullable=False)
    ratingStars = db.Column(db.Integer, nullable=False)
    reviewComment = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='reviews')
    accommodation = db.relationship('Accommodation', back_populates='reviews')