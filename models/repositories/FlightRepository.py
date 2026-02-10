from models import db, Flight

class FlightRepository:
    def __init__(self):
        pass

    def getAll(self):
        return Flight.query.all()

    def getById(self, id):
        return Flight.query.get(id)

    def save(self, flight):
        if flight.id is None:
            db.session.add(flight)

        db.session.commit()

    def delete(self, id):
        flight = self.getById(id)
        if flight:
            db.session.delete(flight)
            db.session.commit()