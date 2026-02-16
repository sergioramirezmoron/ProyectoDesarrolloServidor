# models/UserTrip.py
# User's custom trip with multiple services
from datetime import datetime
from decimal import Decimal
from . import db

class UserTrip(db.Model):
    __tablename__ = 'user_trip'
    
    idUserTrip = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    tripName = db.Column(db.String(200), nullable=False)
    totalPrice = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.Enum('draft', 'confirmed', 'completed', 'cancelled', name='user_trip_status'), 
                       default='draft', nullable=False)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('user_trips', lazy=True))
    items = db.relationship('TripItem', backref='user_trip', lazy=True, cascade='all, delete-orphan')
    
    def calculate_total(self):
        """Calculate total price from all trip items"""
        total = Decimal('0.00')
        for item in self.items:
            if item.itemPrice:
                total += Decimal(str(item.itemPrice))
        self.totalPrice = total
        return total
    
    def get_items_by_type(self, item_type):
        """Get all items of a specific type"""
        return [item for item in self.items if item.itemType == item_type]
    
    def __repr__(self):
        return f'<UserTrip {self.idUserTrip}: {self.tripName} - {self.status}>'
