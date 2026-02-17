# controllers/carController.py
# Fleet Management Controller - For companies to manage their vehicles

from datetime import datetime
from decimal import Decimal, InvalidOperation

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from models import db, Car, User, CarRental

carBlueprint = Blueprint("car", __name__, url_prefix="/fleet")

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


# List all cars in company's fleet
@carBlueprint.get("/")
def list_cars():
    user = get_current_user()
    
    if not user or user.role not in ["admin", "company"]:
        flash("Debes iniciar sesión como empresa para gestionar tu flota.", "warning")
        return redirect(url_for("userBp.login"))
    
    # Companies see only their cars, admins see all
    if user.role == "admin":
        cars = Car.query.filter_by(isActive=True).order_by(Car.createdAt.desc()).all()
    else:
        cars = Car.query.filter_by(idCompany=user.idUser, isActive=True).order_by(Car.createdAt.desc()).all()
    
    return render_template("car/index.html", cars=cars, user=user)


# Show form to create a new car
@carBlueprint.get("/new")
def show_create_form():
    user = get_current_user()
    if not user or user.role not in ["admin", "company"]:
        flash("Permiso denegado.", "danger")
        return redirect(url_for("userBp.login"))
    
    return render_template("car/form.html", car=None, user=user)


# Create a new car
@carBlueprint.post("/create")
def create_car():
    user = get_current_user()
    if not user or user.role not in ["admin", "company"]:
        flash("Permiso denegado.", "danger")
        return redirect(url_for("userBp.login"))

    try:
        brand = request.form["brand"].strip()
        model = request.form["model"].strip()
        maxPeople = int(request.form["maxPeople"])
        pricePerDay = Decimal(request.form["pricePerDay"])
        
        # Handle Image Upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # Create uploads folder if not exists
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        car = Car(
            brand=brand,
            model=model,
            maxPeople=maxPeople,
            pricePerDay=pricePerDay,
            image=image_filename,
            idCompany=user.idUser,
            isActive=True
        )

        db.session.add(car)
        db.session.commit()
        flash(f"Vehículo {car.brand} {car.model} añadido a tu flota exitosamente.", "success")
        return redirect(url_for("car.list_cars"))

    except (KeyError, ValueError, InvalidOperation) as ex:
        db.session.rollback()
        flash(f"Error al crear el vehículo: {str(ex)}", "danger")
        return redirect(url_for("car.show_create_form"))


# View car details
@carBlueprint.get("/<int:idCar>")
def view_car(idCar: int):
    car = Car.query.get_or_404(idCar)
    return render_template("car/detail.html", car=car)


# Show edit form
@carBlueprint.get("/<int:idCar>/edit")
def show_edit_form(idCar: int):
    user = get_current_user()
    if not user or user.role not in ["admin", "company"]:
        flash("Permiso denegado.", "danger")
        return redirect(url_for("userBp.login"))
    
    car = Car.query.get_or_404(idCar)
    
    # Check ownership
    if user.role == "company" and car.idCompany != user.idUser:
        flash("No puedes editar vehículos de otras empresas.", "danger")
        return redirect(url_for("car.list_cars"))
    
    return render_template("car/form.html", car=car, user=user)


# Update car
@carBlueprint.post("/<int:idCar>/edit")
def update_car(idCar: int):
    user = get_current_user()
    if not user or user.role not in ["admin", "company"]:
        flash("Permiso denegado.", "danger")
        return redirect(url_for("userBp.login"))

    car = Car.query.get_or_404(idCar)
    
    # Check ownership
    if user.role == "company" and car.idCompany != user.idUser:
        flash("No puedes editar vehículos de otras empresas.", "danger")
        return redirect(url_for("car.list_cars"))

    try:
        car.brand = request.form["brand"].strip()
        car.model = request.form["model"].strip()
        car.maxPeople = int(request.form["maxPeople"])
        car.pricePerDay = Decimal(request.form["pricePerDay"])
        
        # Handle Image Upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                car.image = filename

        db.session.commit()
        flash(f"Vehículo {car.brand} {car.model} actualizado exitosamente.", "success")
        return redirect(url_for("car.view_car", idCar=car.idCar))

    except (KeyError, ValueError, InvalidOperation) as ex:
        db.session.rollback()
        flash(f"Error al actualizar: {str(ex)}", "danger")
        return redirect(url_for("car.show_edit_form", idCar=idCar))


# Delete car (soft delete)
@carBlueprint.post("/<int:idCar>/delete")
def delete_car(idCar: int):
    user = get_current_user()
    if not user or user.role not in ["admin", "company"]:
        flash("Permiso denegado.", "danger")
        return redirect(url_for("userBp.login"))

    car = Car.query.get_or_404(idCar)
    
    # Check ownership
    if user.role == "company" and car.idCompany != user.idUser:
        flash("No puedes eliminar vehículos de otras empresas.", "danger")
        return redirect(url_for("car.list_cars"))

    try:
        # Soft delete
        car.isActive = False
        db.session.commit()
        flash(f"Vehículo {car.brand} {car.model} eliminado de tu flota.", "success")
    except Exception as ex:
        db.session.rollback()
        flash(f"Error al eliminar: {str(ex)}", "danger")
    
    return redirect(url_for("car.list_cars"))


# --- RENTAL MANAGEMENT (APPROVALS) ---

@carBlueprint.get("/rentals")
def list_rentals():
    """List all rentals for cars owned by the company"""
    user = get_current_user()
    if not user or user.role not in ["admin", "company"]:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("userBp.login"))
    
    # Get rentals for cars belonging to this company
    if user.role == "admin":
        rentals = CarRental.query.order_by(CarRental.createdAt.desc()).all()
    else:
        # Join with Car to filter by company
        rentals = CarRental.query.join(Car).filter(Car.idCompany == user.idUser).order_by(CarRental.createdAt.desc()).all()
    
    # Check for conflicts for pending rentals
    conflicts = {}
    for r in rentals:
        if r.status == 'pending':
            # Use the model method for consistency
            if not r.car.is_available(r.startDate, r.endDate, exclude_id=r.idCarRental):
                conflicts[r.idCarRental] = True

    return render_template("car/rentals.html", rentals=rentals, user=user, conflicts=conflicts)


@carBlueprint.post("/rentals/<int:idRental>/accept")
def accept_rental(idRental: int):
    """Accept a pending rental"""
    user = get_current_user()
    if not user or user.role not in ["admin", "company"]:
        return redirect(url_for("userBp.login"))
    
    rental = CarRental.query.get_or_404(idRental)
    car = rental.car
    
    # Security check
    if user.role == "company" and car.idCompany != user.idUser:
        flash("No tienes permiso.", "danger")
        return redirect(url_for("car.list_rentals"))
    
    # Double check for availability (conflict detection)
    if not car.is_available(rental.startDate, rental.endDate, exclude_id=idRental):
        flash("No se puede aceptar: Existe un conflicto de fechas con una reserva ya confirmada.", "warning")
        return redirect(url_for("car.list_rentals"))
    
    rental.status = 'confirmed'
    db.session.commit()
    flash(f"Reserva para {car.brand} {car.model} confirmada.", "success")
    return redirect(url_for("car.list_rentals"))


@carBlueprint.post("/rentals/<int:idRental>/reject")
def reject_rental(idRental: int):
    """Reject/Cancel a pending rental from the owner side"""
    user = get_current_user()
    if not user or user.role not in ["admin", "company"]:
        return redirect(url_for("userBp.login"))
    
    rental = CarRental.query.get_or_404(idRental)
    
    # Security check
    if user.role == "company" and rental.car.idCompany != user.idUser:
        flash("No tienes permiso.", "danger")
        return redirect(url_for("car.list_rentals"))
    
    rental.status = 'cancelled'
    db.session.commit()
    flash("Reserva denegada correctamente.", "info")
    return redirect(url_for("car.list_rentals"))
