from .db import db

class Rooms(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    idAccommodation = db.Column(db.Integer, db.ForeignKey('accommodations.id'), nullable=False)
    roomNumber = db.Column(db.String(20), nullable=True)
    type = db.Column(db.String(20), nullable=False)
    priceNight = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    def __init__(self, idAccommodation, roomNumber, type, priceNight, capacity):
        self.idAccommodation = idAccommodation
        self.roomNumber = roomNumber
        self.type = type
        self.priceNight = priceNight
        self.capacity = capacity
    

# Metodos para obtener habitaciones
    def getRooms(self):
        return Rooms.query.all()
    
    def getRoom(self, id):
        return Rooms.query.get(id)
    
    def getType(self, type):
        return Rooms.query.filter_by(type=type).all()
    
    def getPriceNight(self, priceNight):
        return Rooms.query.filter_by(priceNight=priceNight).all()
    
    def getCapacity(self, capacity):
        return Rooms.query.filter_by(capacity=capacity).all()

# Metodos para actualizar habitaciones
    def setRoomNumber(self, roomNumber):
        self.roomNumber = roomNumber
    
    def setType(self, type):
        self.type = type
    
    def setPriceNight(self, priceNight):
        self.priceNight = priceNight
    
    def setCapacity(self, capacity):
        self.capacity = capacity