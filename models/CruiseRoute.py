from .db import db

class CruiseRoute(db.Model):
    __tablename__ = "cruise_route"

    idCruiseRoute = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Debe ser Integer y apuntar a cruise_ships.idCruise
    idCruise = db.Column(db.Integer, db.ForeignKey("cruise_ships.idCruise"), nullable=False)
    
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    
    # FKs a Location
    idStartLocation = db.Column(db.Integer, db.ForeignKey("location.idLocation"), nullable=False)
    idEndLocation = db.Column(db.Integer, db.ForeignKey("location.idLocation"), nullable=False)
    
    description = db.Column(db.String(255), nullable=False)
    
    # Relación con las paradas
    stops = db.relationship("CruiseStops", back_populates="cruiseRoute", cascade="all, delete-orphan")
    
    # Relación con los segmentos de precio
    segments = db.relationship("CruiseSegment", backref="route", cascade="all, delete-orphan")

    def __init__(self, idCruise, startDate, endDate, idStartLocation, idEndLocation, description):
        self.idCruise = idCruise
        self.startDate = startDate
        self.endDate = endDate
        self.idStartLocation = idStartLocation
        self.idEndLocation = idEndLocation
        self.description = description