from .db import db
   
class Accommodations(db.Model):
    __tablename__ = 'accommodations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    address = db.Column(db.String(120), unique=False, nullable=False)
    phoneNumber = db.Column(db.String(20), unique=False, nullable=False)
    web = db.Column(db.String(120), unique=False, nullable=False)
    stars_quality = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=False)
    type = db.Column(db.String(20), unique=False, nullable=False)
    idCompany = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    def __init__(self, name, address, phoneNumber, web, stars_quality, description, type, idCompany):
        self.name = name
        self.address = address
        self.phoneNumber = phoneNumber
        self.web = web
        self.stars_quality = stars_quality
        self.description = description
        self.type = type
        self.idCompany = idCompany

    # Metodos para obtener alojamientos
    def getAccommodations(self):
        return Accommodations.query.all()
    
    def getAccommodation(self, id):
        return Accommodations.query.get(id)
    
    def getType(self, type):
        return Accommodations.query.filter_by(type=type).all()
    
    def getStarsQuality(self, stars_quality):
        return Accommodations.query.filter_by(stars_quality=stars_quality).all()
    
    def getDescription(self, description):
        return Accommodations.query.filter_by(description=description).all()
    
    def getPhoneNumber(self, phoneNumber):
        return Accommodations.query.filter_by(phoneNumber=phoneNumber).all()
    
    def getWeb(self, web):
        return Accommodations.query.filter_by(web=web).all()
    
    def getIdCompany(self, idCompany):
        return Accommodations.query.filter_by(idCompany=idCompany).all()
    
    # Metodos para actualizar alojamientos
    def setAccommodation(self, accommodation):
        self.accommodation = accommodation
    
    def setType(self, type):
        self.type = type
    
    def setStarsQuality(self, stars_quality):
        self.stars_quality = stars_quality
    
    def setDescription(self, description):
        self.description = description
    
    def setPhoneNumber(self, phoneNumber):
        self.phoneNumber = phoneNumber
    
    def setWeb(self, web):
        self.web = web
    
    def setIdCompany(self, idCompany):
        self.idCompany = idCompany