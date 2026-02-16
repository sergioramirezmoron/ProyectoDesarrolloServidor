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

    def to_dict(self):
        return {
            'id': self.id,
            'idAccommodation': self.idAccommodation,
            'roomNumber': self.roomNumber,
            'type': self.type,
            'priceNight': float(self.priceNight),
            'capacity': self.capacity
        }