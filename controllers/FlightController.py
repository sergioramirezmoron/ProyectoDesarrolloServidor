from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Flight, User
from datetime import datetime

flight_bp = Blueprint('flight', __name__, url_prefix='/flights')

@flight_bp.route('/', methods=['GET'])
def list_flights():
    flights = Flight.query.all()
    user_id = session.get('userId')
    user = User.query.get(user_id) if user_id else None
    return render_template('flight/index.html', flights=flights, user=user)

@flight_bp.route('/create', methods=['GET', 'POST'])
def create_flight():
    user_id = session.get('userId')
    if not user_id:
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for('userBp.login'))
        
    user = User.query.get(user_id)
    if user.role != 'company' and user.role != 'admin':
        flash("No tienes permisos", "danger")
        return redirect(url_for('flight.list_flights'))

    if request.method == 'POST':
        try:
            flight = Flight(
                aeroline=request.form.get('aeroline'),
                startLocation=int(request.form.get('startLocation')),
                endLocation=int(request.form.get('endLocation')),
                startDate=datetime.strptime(request.form.get('startDate'), '%Y-%m-%dT%H:%M'),
                endDate=datetime.strptime(request.form.get('endDate'), '%Y-%m-%dT%H:%M'),
                price=float(request.form.get('price')),
                maxOccupants=int(request.form.get('maxOccupants')),
                idCompany=user.idUser
            )
            db.session.add(flight)
            db.session.commit()
            flash("Vuelo creado correctamente", "success")
            return redirect(url_for('flight.list_flights'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear vuelo: {str(e)}", "danger")

    return render_template('flight/form.html', user=user)
