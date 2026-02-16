# Autor: Mateo Saez
# Fecha: 2026-02-10

from .db import db

class CruiseRoute(db.Model):
    __tablename__ = "cruise_route"

    idCruiseRoute = db.Column(db.Integer, primary_key=True)
    idCruise = db.Column(db.Integer, db.ForeignKey("cruise.idCruise"))
    idRoute = db.Column(db.Integer, db.ForeignKey("route.idRoute"))
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    startLocation = db.Column(db.String(255), db.ForeignKey("location.idLocation"), nullable=False)
    endLocation = db.Column(db.String(255), db.ForeignKey("location.idLocation"), nullable=False)
    description = db.Column(db.String(255), nullable=False)