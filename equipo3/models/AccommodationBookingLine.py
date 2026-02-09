from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AccommodationBookingLine(db.Model):
    __tablename__ = 'accommodationBookingLine'

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    accommodationId = db.Column(db.Integer, db.ForeignKey('accommodations.id', ondelete='CASCADE'), nullable=False)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    totalPrice = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    bookingDate = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional relationships
    user = db.relationship('User', backref='bookings')
    accommodation = db.relationship('Accommodation', backref='bookings')
