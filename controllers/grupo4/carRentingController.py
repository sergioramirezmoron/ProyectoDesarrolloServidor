# controllers/carRentingController.py

from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.carRenting import db, CarRenting

# This blueprint groups all routes for car renting.
carRentingBlueprint = Blueprint("carRenting", __name__, url_prefix="/car-renting")


# This function converts a text date into a datetime object.
def parse_datetime(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y/%m/%d %H:%M:%S")


# This route shows the list of all rents.
@carRentingBlueprint.get("/")
def list_rents():
    rents = CarRenting.query.order_by(CarRenting.idRent.desc()).all()
    return render_template("carRenting/index.html", rents=rents)


# This route shows the create form.
@carRentingBlueprint.get("/create")
def show_create_form():
    return render_template("carRenting/form.html", rent=None)


# This route creates a new rent from the form data.
@carRentingBlueprint.post("/create")
def create_rent():
    try:
        rent = CarRenting(
            maxPeople=int(request.form["maxPeople"]),
            brand=request.form["brand"].strip(),
            model=request.form["model"].strip(),
            startDate=parse_datetime(request.form["startDate"]),
            endDate=parse_datetime(request.form["endDate"]),
            price=Decimal(request.form["price"]),
            image=(request.form.get("image", "").strip() or None),
        )
        rent.validate_dates()

        db.session.add(rent)
        db.session.commit()
        flash("Rent created successfully.", "success")
        return redirect(url_for("carRenting.list_rents"))

    except (KeyError, ValueError, InvalidOperation) as ex:
        db.session.rollback()
        flash(str(ex), "danger")
        return redirect(url_for("carRenting.show_create_form"))


# This route shows the details of one rent.
@carRentingBlueprint.get("/<int:idRent>")
def view_rent(idRent: int):
    rent = CarRenting.query.get_or_404(idRent)
    return render_template("carRenting/detail.html", rent=rent)


# This route shows the edit form for one rent.
@carRentingBlueprint.get("/<int:idRent>/edit")
def show_edit_form(idRent: int):
    rent = CarRenting.query.get_or_404(idRent)
    return render_template("carRenting/form.html", rent=rent)


# This route updates one rent using the form data.
@carRentingBlueprint.post("/<int:idRent>/edit")
def update_rent(idRent: int):
    rent = CarRenting.query.get_or_404(idRent)

    try:
        rent.maxPeople = int(request.form["maxPeople"])
        rent.brand = request.form["brand"].strip()
        rent.model = request.form["model"].strip()
        rent.startDate = parse_datetime(request.form["startDate"])
        rent.endDate = parse_datetime(request.form["endDate"])
        rent.price = Decimal(request.form["price"])
        rent.image = (request.form.get("image", "").strip() or None)

        rent.validate_dates()

        db.session.commit()
        flash("Rent updated successfully.", "success")
        return redirect(url_for("carRenting.view_rent", idRent=rent.idRent))

    except (KeyError, ValueError, InvalidOperation) as ex:
        db.session.rollback()
        flash(str(ex), "danger")
        return redirect(url_for("carRenting.show_edit_form", idRent=idRent))


# This route deletes one rent by its id.
@carRentingBlueprint.post("/<int:idRent>/delete")
def delete_rent(idRent: int):
    rent = CarRenting.query.get_or_404(idRent)

    try:
        db.session.delete(rent)
        db.session.commit()
        flash("Rent deleted successfully.", "success")
    except Exception as ex:
        db.session.rollback()
        flash(str(ex), "danger")

    return redirect(url_for("carRenting.list_rents"))

