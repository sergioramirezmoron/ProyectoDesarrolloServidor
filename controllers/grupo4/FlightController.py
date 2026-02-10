from models.flight_repository import FlightRepository
from models.flight import Flight
from datetime import datetime

class FlightController:
    """
    Flight Controller
    Handles business logic and user requests for Flights.
    Interacts with the Repository and Session.
    """
    def __init__(self):
        self.repository = FlightRepository()

    def index(self, user_role='user'):
        """Encapsulates logic to list all flights."""
        flights = self.repository.getAll()
        return flights, user_role

    def book_flight(self, id, idClient):
        """
        Handles the booking of a flight.
        """
        flight = self.repository.getById(id)
        if flight:
            # Logic to create booking would go here
            print(f"Flight {flight.id} booked for client {idClient}")
            return True
        return False

    def create(self, data, idCompany):
        """
        Creates a new Flight from form data.
        """
        flight = Flight(
            id=None,
            aeroline=data.get('aeroline'),
            startLocation=int(data.get('startLocation')),
            endLocation=int(data.get('endLocation')),
            startDate=data.get('startDate'),
            endDate=data.get('endDate'),
            price=float(data.get('price')),
            maxOccupants=int(data.get('maxOccupants')),
            idCompany=idCompany
        )
        self.repository.save(flight)
        return flight

    def edit(self, id, data, requester_role, requester_id):
        """
        Updates an existing Flight.
        Checks if requester is Admin or the Owner of the flight.
        """
        flight = self.repository.getById(id)
        if not flight:
            return None

        # Permission Check
        if requester_role != 'admin' and flight.idCompany != requester_id:
            return False # Unauthorized

        flight.aeroline = data.get('aeroline')
        flight.startLocation = int(data.get('startLocation'))
        flight.endLocation = int(data.get('endLocation'))
        flight.startDate = data.get('startDate')
        flight.endDate = data.get('endDate')
        flight.price = float(data.get('price'))
        flight.maxOccupants = int(data.get('maxOccupants'))
        
        self.repository.save(flight)
        return flight

    def delete(self, id, requester_role, requester_id):
        """
        Deletes a flight by ID.
        Checks if requester is Admin or the Owner.
        """
        flight = self.repository.getById(id)
        if not flight:
            return False

        # Permission Check
        if requester_role != 'admin' and flight.idCompany != requester_id:
            return False # Unauthorized

        self.repository.delete(id)
        return True
    
    def get_flight(self, id):
        """Helper to get a single flight for editing."""
        return self.repository.getById(id)
