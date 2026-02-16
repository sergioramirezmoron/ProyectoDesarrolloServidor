from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models.db import db


class AccommodationBookingLine(db.Model):
    __tablename__ = 'accommodation_booking_line'

    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    idAccommodation = db.Column(db.Integer, db.ForeignKey('accommodation.id', ondelete='CASCADE'), nullable=False)
    idRoom = db.Column(db.Integer, db.ForeignKey('room.id', ondelete='CASCADE'), nullable=True) # Making it optional for now to avoid breaking existing data, but intended for use
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    totalPrice = db.Column(db.Numeric(10, 2), nullable=False)

    room = db.relationship('Room', backref='bookings')
    status = db.Column(db.String(20), default='pending')
    bookingDate = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='bookings')
    accommodation = db.relationship('Accommodation', back_populates='bookings')