from .db import db

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False)
    
    def __init__(self, country, city):
        self.country = country
        self.city = city

    # Metodos para obtener ubicaciones
    def getLocations(self):
        return Location.query.all()
    
    def getLocation(self, id):
        return Location.query.get(id)
    
    def getCountry(self, country):
        return Location.query.filter_by(country=country).all()
    
    def getCity(self, city):
        return Location.query.filter_by(city=city).all()
    
    # Metodos para actualizar ubicaciones
    def setCountry(self, country):
        self.country = country
    
    def setCity(self, city):
        self.city = city