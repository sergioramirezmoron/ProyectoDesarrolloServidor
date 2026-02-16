from .db import db

class Cruise(db.Model):
    __tablename__ = 'cruises'
    # Definimos idCruise como Primary Key única
    idCruise = db.Column(db.Integer, primary_key=True, autoincrement=True)
    startLocation = db.Column(db.String(50), nullable=False)
    endLocation = db.Column(db.String(50), nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, startLocation, endLocation, startDate, endDate, description, idCruise=None):
        self.idCruise = idCruise
        self.startLocation = startLocation
        self.endLocation = endLocation
        self.startDate = startDate
        self.endDate = endDate
        self.description = description

    def to_dict(self):
        return {
            "idCruise": self.idCruise,
            "startLocation": self.startLocation,
            "endLocation": self.endLocation,
            "startDate": self.startDate.isoformat(),
            "endDate": self.endDate.isoformat(),
            "description": self.description
        }