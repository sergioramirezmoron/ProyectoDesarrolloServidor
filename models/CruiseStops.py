# Autor: Mateo Saez
# Fecha: 2026-02-10

from .db import db

class CruiseStops(db.Model):
    __tablename__ = "cruise_stops"
    
    idCruiseStop = db.Column(db.Integer, primary_key=True)
    idCruiseRoute = db.Column(db.Integer, db.ForeignKey("cruise_route.idCruiseRoute"))
    idLocation = db.Column(db.Integer, db.ForeignKey("location.idLocation"))
    stopOrder = db.Column(db.Integer, nullable=False)
    arrivalDate = db.Column(db.DateTime, nullable=False) #Cuando un pasajero sube al barco
    departureDate = db.Column(db.DateTime, nullable=False)

    cruiseRoute = db.relationship("CruiseRoute", back_populates="stops")
    location = db.relationship("Location", back_populates="stops")

    def toDict(self):
        return {
            "idCruiseStop": self.idCruiseStop,
            "idCruiseRoute": self.idCruiseRoute,
            "idLocation": self.idLocation,
            "stopOrder": self.stopOrder,
            "arrivalDate": self.arrivalDate,
            "departureDate": self.departureDate
        }
    