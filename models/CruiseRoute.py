# Autor: Mateo Saez
# Fecha: 2026-02-10

from .db import db

class CruiseRoute(db.Model):
    __tablename__ = "cruise_route"

    idCruiseRoute = db.Column(db.Integer, primary_key=True)
    idCruise = db.Column(db.Integer, db.ForeignKey("cruise.idCruise"))
    idRoute = db.Column(db.Integer, db.ForeignKey("route.idRoute"))
    idStop = db.Column(db.Integer, db.ForeignKey("cruise_stop.idCruiseStop"))
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    startLocation = db.Column(db.String(255), db.ForeignKey("location.idLocation"), nullable=False)
    endLocation = db.Column(db.String(255), db.ForeignKey("location.idLocation"), nullable=False)
    description = db.Column(db.String(255), nullable=False)

    cruise = db.relationship("Cruise", back_populates="routes")
    route = db.relationship("Route", back_populates="routes")
    startLocation = db.relationship("Location", back_populates="routes")
    endLocation = db.relationship("Location", back_populates="routes")
    stops = db.relationship("CruiseStop", back_populates="route")


    def toDict(self):
        return {
            "idCruiseRoute": self.idCruiseRoute,
            "idCruise": self.idCruise,
            "idRoute": self.idRoute,
            "idStop": self.idStop,
            "startDate": self.startDate,
            "endDate": self.endDate,
            "startLocation": self.startLocation,
            "endLocation": self.endLocation,
            "description": self.description
        }