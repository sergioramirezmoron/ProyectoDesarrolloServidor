from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models import BusTrain
from models import db, Location, User

transport_bp = Blueprint("transport", __name__, url_prefix="/transports")

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)

@transport_bp.route("/", methods=["GET"])
def list_transports():
    user = get_current_user()
    transports = BusTrain.query.all()
    return render_template("infoTransports.html", transports=transports, user=user)

@transport_bp.route("/my", methods=["GET"])
def my_transports():
    user = get_current_user()
    if not user or user.role != "company":
        flash("Solo las compañías pueden ver sus transportes.")
        return redirect(url_for("transport.list_transports"))
    transports = BusTrain.query.filter_by(idCompany=user.idUser).all()
    return render_template("myTransports.html", transports=transports, user=user)

@transport_bp.route("/create", methods=["GET", "POST"])
def create_transport():
    user = get_current_user()
    if not user or user.role != "company":
        flash("Solo las compañías pueden crear transportes.")
        return redirect(url_for("transport.list_transports"))
    locations = Location.query.all()
    if request.method == "POST":
        type = request.form["type"]
        idLocationStart = request.form["idLocationStart"]
        idLocationEnd = request.form["idLocationEnd"]
        startDate = datetime.strptime(request.form["startDate"], "%Y-%m-%dT%H:%M")
        endDate = datetime.strptime(request.form["endDate"], "%Y-%m-%dT%H:%M")
        price = float(request.form["price"])
        transport = BusTrain(type=type, idCompany=user.idUser, idLocationStart=idLocationStart, idLocationEnd=idLocationEnd, startDate=startDate, endDate=endDate, price=price)
        db.session.add(transport)
        db.session.commit()
        flash("¡Transporte creado!")
        return redirect(url_for("transport.my_transports"))
    return render_template("formTransport.html", locations=locations, user=user)
