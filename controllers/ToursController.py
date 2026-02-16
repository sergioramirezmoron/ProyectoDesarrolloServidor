from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models.Tour import Tour
from models import db, Location, User

tour_bp = Blueprint("tour", __name__, url_prefix="/tours")

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)

@tour_bp.route("/", methods=["GET"])
def list_tours():
    user = get_current_user()
    tours = Tour.query.all()
    return render_template("tour_list.html", tours=tours, user=user)

@tour_bp.route("/my", methods=["GET"])
def my_tours():
    user = get_current_user()
    if not user or user.role != "company":
        flash("Solo las compañías pueden ver sus tours.")
        return redirect(url_for("tour.list_tours"))
    tours = Tour.query.filter_by(idCompany=user.idUser).all()
    return render_template("my_tours.html", tours=tours, user=user)

@tour_bp.route("/create", methods=["GET", "POST"])
def create_tour():
    user = get_current_user()
    if not user or user.role != "company":
        flash("Solo las compañías pueden crear tours.")
        return redirect(url_for("tour.list_tours"))
    locations = Location.query.all()
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        image = request.form["image"]
        price = float(request.form["price"])
        startDate = datetime.strptime(request.form["startDate"], "%Y-%m-%dT%H:%M")
        endDate = datetime.strptime(request.form["endDate"], "%Y-%m-%dT%H:%M")
        idLocation = request.form["idLocation"]
        tour = Tour(title=title, description=description, image=image, price=price, startDate=startDate, endDate=endDate, idLocation=idLocation, idCompany=user.idUser)
        db.session.add(tour)
        db.session.commit()
        flash("¡Tour creado!")
        return redirect(url_for("tour.my_tours"))
    return render_template("tour_form.html", locations=locations, user=user)
