from models.db import db

# -------------------------------------------------------------------
# CLASE ROOM (HABITACIONES)
# -------------------------------------------------------------------
class Room(db.Model):
    __tablename__ = 'room'

    id = db.Column(db.Integer, primary_key=True)
    idAccommodation = db.Column(db.Integer, db.ForeignKey('accommodation.id', ondelete='CASCADE'), nullable=False)
    roomNumber = db.Column(db.String(10), nullable=True)
    type = db.Column(db.String(50))
    priceNight = db.Column(db.Numeric(8, 2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    accommodation = db.relationship('Accommodation', backref='rooms')

    def is_available(self, start_date, end_date):
        """
        Check if this room is available for the given date range.
        Returns True if no confirmed bookings overlap with the dates.
        """
        from .AccommodationBookingLine import AccommodationBookingLine
        
        overlapping_bookings = AccommodationBookingLine.query.filter(
            AccommodationBookingLine.idRoom == self.id,
            AccommodationBookingLine.status == 'confirmed',
            AccommodationBookingLine.startDate < end_date,
            AccommodationBookingLine.endDate > start_date
        ).count()
        
        return overlapping_bookings == 0

    def to_dict(self):
        return {
            'id': self.id,
            'idAccommodation': self.idAccommodation,
            'roomNumber': self.roomNumber,
            'type': self.type,
            'priceNight': float(self.priceNight),
            'capacity': self.capacity
        }