# controllers/carRentingController.py
# Rental Booking Controller - For users to browse and rent vehicles

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

<<<<<<< HEAD
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Car, CarRental, User
=======
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, CarRenting
import os
from werkzeug.utils import secure_filename
>>>>>>> 4168c0925220e68bf1093d69348bfc81e4783bd5

carRentingBlueprint = Blueprint("carRental", __name__, url_prefix="/car-rental")

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def parse_datetime(date_str):
    """Parse datetime string in format Y/m/d H:i:S"""
    try:
        return datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S")
    except ValueError:
        raise ValueError(f"Formato de fecha inválido: {date_str}. Use YYYY/MM/DD HH:MM:SS")


# Browse available cars for rental
@carRentingBlueprint.get("/")
@carRentingBlueprint.get("/browse")
def browse_cars():
    """Show all available cars that can be rented"""
    # Get all active cars
    cars = Car.query.filter_by(isActive=True).order_by(Car.createdAt.desc()).all()
    return render_template("carRental/browse.html", cars=cars)


# View car details (for potential renters)
@carRentingBlueprint.get("/car/<int:idCar>")
def view_car_for_rental(idCar: int):
    """View a specific car's details for rental"""
    car = Car.query.get_or_404(idCar)
    return render_template("carRental/detail.html", car=car)


# Show booking form for a specific car
@carRentingBlueprint.get("/car/<int:idCar>/book")
def show_booking_form(idCar: int):
    """Show the booking form for a specific car"""
    user = get_current_user()
    if not user:
        flash("Debes iniciar sesión para reservar un vehículo.", "warning")
        return redirect(url_for("userBp.login"))
    
    car = Car.query.get_or_404(idCar)
    return render_template("carRental/book.html", car=car, user=user)


# Create a rental booking
@carRentingBlueprint.post("/car/<int:idCar>/book")
def create_booking(idCar: int):
    """Create a new rental booking"""
    user = get_current_user()
    if not user:
        flash("Debes iniciar sesión para reservar.", "danger")
        return redirect(url_for("userBp.login"))
    
    car = Car.query.get_or_404(idCar)
    
    try:
<<<<<<< HEAD
        start_date = parse_datetime(request.form["startDate"])
        end_date = parse_datetime(request.form["endDate"])
        
        # Validate dates
        if end_date <= start_date:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")
        
        # Allow a 15-minute grace period for "past" dates to account for server/client lag
        grace_period = timedelta(minutes=15)
        if start_date < (datetime.now() - grace_period):
            server_time = datetime.now().strftime("%H:%M")
            raise ValueError(f"La fecha de inicio no puede ser en el pasado (Hora servidor: {server_time}).")
        
        # Check availability
        if not car.is_available(start_date, end_date):
            flash("Este vehículo no está disponible para las fechas seleccionadas.", "warning")
            return redirect(url_for("carRental.show_booking_form", idCar=idCar))
        
        # Calculate total price
        days = (end_date - start_date).days
        if days < 1:
            days = 1
        total_price = Decimal(days) * car.pricePerDay
        
        # Create rental
        rental = CarRental(
            idCar=car.idCar,
            idUser=user.idUser,
            startDate=start_date,
            endDate=end_date,
            totalPrice=total_price,
            status='pending'
        )
        
        db.session.add(rental)
=======
        rent = CarRenting(
            maxPeople=int(request.form["maxPeople"]),
            brand=request.form["brand"].strip(),
            model=request.form["model"].strip(),
            startDate=parse_datetime(request.form["startDate"]),
            endDate=parse_datetime(request.form["endDate"]),
            price=Decimal(request.form["price"]),
        )

        # Handle Image Upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                rent.image = filename

        rent.validate_dates()

        db.session.add(rent)
>>>>>>> 4168c0925220e68bf1093d69348bfc81e4783bd5
        db.session.commit()
        
        flash(f"¡Reserva creada! Total: {total_price}€ por {days} días.", "success")
        return redirect(url_for("carRental.my_rentals"))
    
    except (KeyError, ValueError, InvalidOperation) as ex:
        db.session.rollback()
        flash(f"Error al crear la reserva: {str(ex)}", "danger")
        return redirect(url_for("carRental.show_booking_form", idCar=idCar))


# View user's rental history
@carRentingBlueprint.get("/my-rentals")
def my_rentals():
    """Show current user's rental bookings"""
    user = get_current_user()
    if not user:
        flash("Debes iniciar sesión para ver tus reservas.", "warning")
        return redirect(url_for("userBp.login"))
    
    rentals = CarRental.query.filter_by(idUser=user.idUser).order_by(CarRental.createdAt.desc()).all()
    return render_template("carRental/my-rentals.html", rentals=rentals, user=user)


# View rental details
@carRentingBlueprint.get("/rental/<int:idCarRental>")
def view_rental(idCarRental: int):
    """View details of a specific rental"""
    rental = CarRental.query.get_or_404(idCarRental)
    
    user = get_current_user()
    # Only the renter or admin can view
    if not user or (user.idUser != rental.idUser and user.role != "admin"):
        flash("No tienes permiso para ver esta reserva.", "danger")
        return redirect(url_for("carRental.browse_cars"))
    
    return render_template("carRental/rental-detail.html", rental=rental)


# Cancel a rental
@carRentingBlueprint.post("/rental/<int:idCarRental>/cancel")
def cancel_rental(idCarRental: int):
    """Cancel a rental booking"""
    user = get_current_user()
    if not user:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("userBp.login"))
    
    rental = CarRental.query.get_or_404(idCarRental)
    
    # Only the renter can cancel
    if user.idUser != rental.idUser:
        flash("No puedes cancelar reservas de otros usuarios.", "danger")
        return redirect(url_for("carRental.my_rentals"))
    
    # Can only cancel pending or confirmed rentals
    if rental.status not in ['pending', 'confirmed']:
        flash("Esta reserva no se puede cancelar.", "warning")
        return redirect(url_for("carRental.my_rentals"))
    
    try:
<<<<<<< HEAD
        rental.status = 'cancelled'
=======
        rent.maxPeople = int(request.form["maxPeople"])
        rent.brand = request.form["brand"].strip()
        rent.model = request.form["model"].strip()
        rent.startDate = parse_datetime(request.form["startDate"])
        rent.endDate = parse_datetime(request.form["endDate"])
        rent.price = Decimal(request.form["price"])

        # Handle Image Upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                rent.image = filename

        rent.validate_dates()

>>>>>>> 4168c0925220e68bf1093d69348bfc81e4783bd5
        db.session.commit()
        flash("Reserva cancelada exitosamente.", "success")
    except Exception as ex:
        db.session.rollback()
        flash(f"Error al cancelar: {str(ex)}", "danger")
    
    return redirect(url_for("carRental.my_rentals"))
