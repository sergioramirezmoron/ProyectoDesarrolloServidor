from .db import db

class Flight(db.Model):
    _tablename_ = 'flight'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aeroline = db.Column(db.String(100), nullable=False)
    startLocation = db.Column(db.Integer, nullable=False)
    endLocation = db.Column(db.Integer, nullable=False)
    startDate = db.Column(db.String(20), nullable=False)
    endDate = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    maxOccupants = db.Column(db.Integer, nullable=False)
    idCompany = db.Column(db.Integer, nullable=False)

    def _init_(self, aeroline, startLocation, endLocation, startDate, endDate, price, maxOccupants, idCompany, id=None):
        self.id = id
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
            "id": self.id,
            "aeroline": self.aeroline,
            "startLocation": self.startLocation,
            "endLocation": self.endLocation,
            "startDate": self.startDate,
            "endDate": self.endDate,
            "price": self.price,
            "maxOccupants": self.maxOccupants,
            "idCompany": self.idCompany
        }