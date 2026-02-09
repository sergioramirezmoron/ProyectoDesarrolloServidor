from datetime import datetime
from models import db

class Review(db.Model):
    __tablename__ = 'resenas'
    
    idReview = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    idAccommodation = db.Column(db.Integer, db.ForeignKey('alojamientos.idAccommodation', ondelete='CASCADE'), nullable=False)
    ratingStars = db.Column(db.Integer, nullable=False)
    reviewComment = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.idReview} - {self.ratingStars} stars>'