# Autor: Sistema Reestructurado
# Fecha: 2026-02-16
from datetime import datetime
from decimal import Decimal
from .db import db

class CarRental(db.Model):
    """
    Represents a rental booking - a user renting a specific car for a period.
    This is separate from the Car itself, allowing one car to have many rentals.
    """
    __tablename__ = "carRental"

    idCarRental = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # What is being rented
    idCar = db.Column(db.Integer, db.ForeignKey('car.idCar'), nullable=False)
    
    # Who is renting
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    
    # When
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    
    # Pricing
    totalPrice = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Status tracking
    status = db.Column(
        db.Enum('pending', 'confirmed', 'completed', 'cancelled', name='rental_status'),
        default='pending',
        nullable=False
    )
    
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    car = db.relationship('Car', back_populates='rentals')
    user = db.relationship('User', foreign_keys=[idUser])
    
    def to_dict(self):
        return {
            "idCarRental": self.idCarRental,
            "idCar": self.idCar,
            "idUser": self.idUser,
            "startDate": self.startDate.strftime("%Y/%m/%d %H:%M:%S"),
            "endDate": self.endDate.strftime("%Y/%m/%d %H:%M:%S"),
            "totalPrice": float(self.totalPrice),
            "status": self.status,
            "createdAt": self.createdAt.strftime("%Y/%m/%d %H:%M:%S"),
            "car": self.car.to_dict() if self.car else None,
        }
    
    def validate_dates(self):
        """Validate that end date is after start date."""
        if self.endDate <= self.startDate:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")
    
    def calculate_total_price(self):
        """Calculate total price based on car's daily rate and rental duration."""
        if self.car and self.startDate and self.endDate:
            days = (self.endDate - self.startDate).days
            if days < 1:
                days = 1  # Minimum 1 day
            self.totalPrice = Decimal(days) * self.car.pricePerDay
    
    def __repr__(self):
        return f'<CarRental {self.idCarRental}: Car {self.idCar} by User {self.idUser}>'
