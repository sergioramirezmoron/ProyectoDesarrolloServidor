# controllers/carController.py
# Fleet Management Controller - For companies to manage their vehicles

from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Car, User

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
        car = Car(
            brand=request.form["brand"].strip(),
            model=request.form["model"].strip(),
            maxPeople=int(request.form["maxPeople"]),
            pricePerDay=Decimal(request.form["pricePerDay"]),
            image=(request.form.get("image", "").strip() or None),
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
        car.image = request.form.get("image", "").strip() or None

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
