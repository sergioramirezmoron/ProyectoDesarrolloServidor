# Autor: Sistema Reestructurado
# Fecha: 2026-02-16
from datetime import datetime
from decimal import Decimal
from .db import db

class Car(db.Model):
    """
    Represents a vehicle in a company's fleet.
    This is the physical car that can be rented multiple times.
    """
    __tablename__ = "car"

    idCar = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Vehicle information
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    maxPeople = db.Column(db.Integer, nullable=False)
    pricePerDay = db.Column(db.Numeric(10, 2), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    
    # Company ownership
    idCompany = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    
    # Status
    isActive = db.Column(db.Boolean, default=True, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    company = db.relationship('User', foreign_keys=[idCompany])
    rentals = db.relationship('CarRental', back_populates='car', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            "idCar": self.idCar,
            "brand": self.brand,
            "model": self.model,
            "maxPeople": self.maxPeople,
            "pricePerDay": float(self.pricePerDay),
            "image": self.image,
            "idCompany": self.idCompany,
            "isActive": self.isActive,
            "createdAt": self.createdAt.strftime("%Y/%m/%d %H:%M:%S"),
        }
    
    def is_available(self, start_date, end_date):
        """
        Check if this car is available for the given date range.
        Returns True if no confirmed rentals overlap with the dates.
        """
        from .CarRental import CarRental
        
        overlapping_rentals = CarRental.query.filter(
            CarRental.idCar == self.idCar,
            CarRental.status.in_(['pending', 'confirmed']),
            CarRental.startDate < end_date,
            CarRental.endDate > start_date
        ).count()
        
        return overlapping_rentals == 0
    
    def __repr__(self):
        return f'<Car {self.brand} {self.model}>'
