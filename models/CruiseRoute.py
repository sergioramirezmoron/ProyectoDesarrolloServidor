from .db import db

class CruiseRoute(db.Model):
    __tablename__ = "cruise_route"

    idCruiseRoute = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Debe ser Integer y apuntar a cruises.idCruise
    idCruise = db.Column(db.Integer, db.ForeignKey("cruises.idCruise"), nullable=False)
    
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    
    # FKs a Location
    idStartLocation = db.Column(db.Integer, db.ForeignKey("location.idLocation"), nullable=False)
    idEndLocation = db.Column(db.Integer, db.ForeignKey("location.idLocation"), nullable=False)
    
    description = db.Column(db.String(255), nullable=False)
    
    stops = db.relationship("CruiseStops", back_populates="cruiseRoute", cascade="all, delete-orphan")

    def __init__(self, idCruise, startDate, endDate, idStartLocation, idEndLocation, description):
        self.idCruise = idCruise
        self.startDate = startDate
        self.endDate = endDate
        self.idStartLocation = idStartLocation
        self.idEndLocation = idEndLocation
        self.description = description