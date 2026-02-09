from models import db # Asumiendo que db se importa desde aquí

# -------------------------------------------------------------------
# CLASE ROOM (HABITACIONES)
# -------------------------------------------------------------------
class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    idAccommodation = db.Column(db.Integer, db.ForeignKey('alojamientos.id'), nullable=False) 
    roomNumber = db.Column(db.String(10), nullable=True)
    type = db.Column(db.String(50))
    priceNight = db.Column(db.Numeric(8, 2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    def __init__(self, idAccommodation, type, priceNight, capacity, roomNumber=None):
        self.idAccommodation = idAccommodation
        self.roomNumber = roomNumber
        self.type = type
        self.priceNight = priceNight
        self.capacity = capacity

    def to_dict(self):
        return {
            'id': self.id,
            'idAccommodation': self.idAccommodation,
            'roomNumber': self.roomNumber,
            'type': self.type,
            'priceNight': float(self.priceNight),
            'capacity': self.capacity
        }