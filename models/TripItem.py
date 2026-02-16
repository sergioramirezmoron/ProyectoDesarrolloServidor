# models/TripItem.py
# Junction table linking UserTrip to various services
from datetime import datetime
from . import db

class TripItem(db.Model):
    __tablename__ = 'trip_item'
    
    idTripItem = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idUserTrip = db.Column(db.Integer, db.ForeignKey('user_trip.idUserTrip'), nullable=False)
    
    # Type of service (accommodation, flight, cruise, car_rental, tour, transport)
    itemType = db.Column(db.Enum('accommodation', 'flight', 'cruise', 'car_rental', 'tour', 'transport', 
                                  name='trip_item_type'), nullable=False)
    
    # ID of the specific booking/service
    itemId = db.Column(db.Integer, nullable=False)
    
    # Price at time of booking (snapshot)
    itemPrice = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Optional: Store item details as JSON for display
    itemDetails = db.Column(db.Text, nullable=True)  # JSON string
    
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<TripItem {self.idTripItem}: {self.itemType} #{self.itemId}>'
