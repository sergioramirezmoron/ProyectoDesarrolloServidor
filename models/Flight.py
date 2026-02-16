from .db import db

class Flight(db.Model):
    __tablename__ = 'flight'

    idFlight = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aeroline = db.Column(db.String(100), nullable=False)
    startLocation = db.Column(db.Integer, db.ForeignKey('location.idLocation'), nullable=False)
    endLocation = db.Column(db.Integer, db.ForeignKey('location.idLocation'), nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    maxOccupants = db.Column(db.Integer, nullable=False)
    idCompany = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)

    # Relaciones
    company = db.relationship('User', foreign_keys=[idCompany])
    locationStart = db.relationship('Location', foreign_keys=[startLocation])
    locationEnd = db.relationship('Location', foreign_keys=[endLocation])

    def __init__(self, aeroline, startLocation, endLocation, startDate, endDate, price, maxOccupants, idCompany, idFlight=None):
        self.idFlight = idFlight
        self.aeroline = aeroline
        self.startLocation = startLocation
        self.endLocation = endLocation
        self.startDate = startDate
        self.endDate = endDate
        self.price = price
        self.maxOccupants = maxOccupants
        self.idCompany = idCompany

    def to_dict(self):
        return {
            "idFlight": self.idFlight,
            "aeroline": self.aeroline,
            "startLocation": self.startLocation,
            "endLocation": self.endLocation,
            "startDate": self.startDate.isoformat() if self.startDate else None,
            "endDate": self.endDate.isoformat() if self.endDate else None,
            "price": self.price,
            "maxOccupants": self.maxOccupants,
            "idCompany": self.idCompany
        }