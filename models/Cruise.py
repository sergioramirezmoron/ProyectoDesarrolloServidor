from .db import db

class Cruise(db.Model):
    __tablename__ = 'cruise_ships'
    
    idCruise = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cruiseName = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    idCompany = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)

    # Relación con las rutas (viajes) que realiza este barco
    routes = db.relationship('CruiseRoute', backref='ship', lazy=True)

    def __init__(self, cruiseName, capacity, idCompany):
        self.cruiseName = cruiseName
        self.capacity = capacity
        self.idCompany = idCompany

    def to_dict(self):
        return {
            "idCruise": self.idCruise,
            "cruiseName": self.cruiseName,
            "capacity": self.capacity,
            "idCompany": self.idCompany
        }