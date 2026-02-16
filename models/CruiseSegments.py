from .db import db

class CruiseSegment(db.Model):
    __tablename__ = 'cruise_segments'

    idSegment = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idRoute = db.Column(db.Integer, db.ForeignKey('cruise_route.idRoute'), nullable=False)
    idStopOrigin = db.Column(db.Integer, db.ForeignKey('cruise_stops.idStop'), nullable=False)
    idStopDestination = db.Column(db.Integer, db.ForeignKey('cruise_stops.idStop'), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, idRoute, idStopOrigin, idStopDestination, price, idSegment=None):
        self.idSegment = idSegment
        self.idRoute = idRoute
        self.idStopOrigin = idStopOrigin
        self.idStopDestination = idStopDestination
        self.price = price

    def to_dict(self):
        return {
            "idSegment": self.idSegment,
            "idRoute": self.idRoute,
            "idStopOrigin": self.idStopOrigin,
            "idStopDestination": self.idStopDestination,
            "price": self.price
        }