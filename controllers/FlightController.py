from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Flight, User
from datetime import datetime

flight_bp = Blueprint('flight', __name__)

@flight_bp.route('/', methods=['GET'])
def list_flights():
    flights = Flight.query.all()
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    return render_template('flight/index.html', flights=flights, user=user)

@flight_bp.route('/create', methods=['GET', 'POST'])
def create_flight():
    user_id = session.get('user_id')
    if not user_id:
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for('userBp.login'))
        
    user = User.query.get(user_id)
    if user.role != 'company' and user.role != 'admin':
        flash("No tienes permisos", "danger")
        return redirect(url_for('flight.list_flights'))

    from models import Location
    locations = Location.query.all()

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

    return render_template('flight/form.html', user=user, locations=locations)

@flight_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_flight(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('userBp.login'))
        
    user = User.query.get(user_id)
    flight = Flight.query.get_or_404(id)
    
    if user.role != 'admin' and (user.role != 'company' or flight.idCompany != user.idUser):
        flash("No tienes permisos", "danger")
        return redirect(url_for('flight.list_flights'))

    from models import Location
    locations = Location.query.all()

    if request.method == 'POST':
        try:
            flight.aeroline = request.form.get('aeroline')
            flight.startLocation = int(request.form.get('startLocation'))
            flight.endLocation = int(request.form.get('endLocation'))
            flight.startDate = datetime.strptime(request.form.get('startDate'), '%Y-%m-%dT%H:%M')
            flight.endDate = datetime.strptime(request.form.get('endDate'), '%Y-%m-%dT%H:%M')
            flight.price = float(request.form.get('price'))
            flight.maxOccupants = int(request.form.get('maxOccupants'))
            
            db.session.commit()
            flash("Vuelo actualizado correctamente", "success")
            return redirect(url_for('flight.list_flights'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar vuelo: {str(e)}", "danger")

    return render_template('flight/form.html', user=user, flight=flight, locations=locations)

@flight_bp.route('/delete/<int:id>', methods=['POST'])
def delete_flight(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('userBp.login'))
        
    user = User.query.get(user_id)
    flight = Flight.query.get_or_404(id)
    
    if user.role != 'admin' and (user.role != 'company' or flight.idCompany != user.idUser):
        flash("No tienes permisos", "danger")
    else:
        try:
            db.session.delete(flight)
            db.session.commit()
            flash("Vuelo eliminado correctamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar vuelo: {str(e)}", "danger")
            
    return redirect(url_for('flight.list_flights'))
