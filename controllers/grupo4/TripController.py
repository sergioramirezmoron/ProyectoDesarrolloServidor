from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.grupo4.Trip import Trip
from models.grupo4.Location import Location
from models.User import User
from datetime import datetime


trip_bp = Blueprint('trip', __name__, url_prefix='/trips')

def _current_role():
    return (session.get('role') or 'USER').upper()

def _current_user_id():
    return session.get('user_id')

def _is_admin(role):
    return role == 'ADMIN'

def _is_company(role):
    return role == 'COMPANY'

def _can_manage_trip(trip, role, user_id):
    if _is_admin(role):
        return True
    return _is_company(role) and user_id is not None and trip.idCompany == user_id

@trip_bp.route('/')
def list_trips():
    """List all trips"""
    trips = Trip.query.all()
    role = _current_role()
    user_id = _current_user_id()
    return render_template(
        'grupo4/trip/trip_list.html',
        trips=trips,
        user_role=role,
        current_user_id=user_id,
    )

@trip_bp.route('/create', methods=['GET', 'POST'])
def create_trip():
    """Create a new trip"""
    role = _current_role()
    user_id = _current_user_id()

    if not (_is_admin(role) or _is_company(role)):
        flash('No tienes permisos para crear viajes.', 'error')
        return redirect(url_for('trip.list_trips'))

    if request.method == 'POST':
        try:
            # Parse datetime from form (format: yyyy/mm/dd hh:mm:ss)
            start_date_str = request.form.get('startDate')
            end_date_str = request.form.get('endDate')
            
            start_date = datetime.strptime(start_date_str, '%Y/%m/%d %H:%M:%S')
            end_date = datetime.strptime(end_date_str, '%Y/%m/%d %H:%M:%S')
            
            # Create new trip
            new_trip = Trip(
                startLocation=int(request.form.get('startLocation')),
                endLocation=int(request.form.get('endLocation')),
                startDate=start_date,
                endDate=end_date,
                occupants=int(request.form.get('occupants')),
                price=float(request.form.get('price')),
                idCompany=int(request.form.get('idCompany')) if _is_admin(role) else user_id
            )

            if _is_company(role) and not user_id:
                raise ValueError('Usuario no identificado para la compania.')
            
            db.session.add(new_trip)
            db.session.commit()
            
            flash('Trip created successfully!', 'success')
            return redirect(url_for('trip.list_trips'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating trip: {str(e)}', 'error')
    
    # Get all locations and companies for the dropdowns
    locations = Location.query.all()
    companies = User.query.filter_by(role='COMPANY').all()
    current_user = User.query.get(user_id) if user_id else None
    return render_template(
        'grupo4/trip/trip_create.html',
        locations=locations,
        companies=companies,
        user_role=role,
        current_user=current_user,
    )

@trip_bp.route('/<int:id>')
def view_trip(id):
    """View trip details"""
    trip = Trip.query.get_or_404(id)
    role = _current_role()
    user_id = _current_user_id()
    return render_template(
        'grupo4/trip/trip_detail.html',
        trip=trip,
        user_role=role,
        current_user_id=user_id,
    )

@trip_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_trip(id):
    """Edit an existing trip"""
    trip = Trip.query.get_or_404(id)
    role = _current_role()
    user_id = _current_user_id()

    if not (_is_admin(role) or _is_company(role)):
        flash('No tienes permisos para editar viajes.', 'error')
        return redirect(url_for('trip.view_trip', id=trip.idTrip))

    if _is_company(role) and trip.idCompany != user_id:
        flash('Solo puedes editar tus propios viajes.', 'error')
        return redirect(url_for('trip.view_trip', id=trip.idTrip))
    
    if request.method == 'POST':
        try:
            # Parse datetime from form
            start_date_str = request.form.get('startDate')
            end_date_str = request.form.get('endDate')
            
            trip.startLocation = int(request.form.get('startLocation'))
            trip.endLocation = int(request.form.get('endLocation'))
            trip.startDate = datetime.strptime(start_date_str, '%Y/%m/%d %H:%M:%S')
            trip.endDate = datetime.strptime(end_date_str, '%Y/%m/%d %H:%M:%S')
            trip.occupants = int(request.form.get('occupants'))
            trip.price = float(request.form.get('price'))
            trip.idCompany = int(request.form.get('idCompany')) if _is_admin(role) else trip.idCompany
            
            db.session.commit()
            
            flash('Trip updated successfully!', 'success')
            return redirect(url_for('trip.view_trip', id=trip.idTrip))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating trip: {str(e)}', 'error')
    
    locations = Location.query.all()
    companies = User.query.filter_by(role='COMPANY').all()
    current_user = User.query.get(user_id) if user_id else None
    return render_template(
        'grupo4/trip/trip_edit.html',
        trip=trip,
        locations=locations,
        companies=companies,
        user_role=role,
        current_user=current_user,
    )

@trip_bp.route('/<int:id>/delete', methods=['POST'])
def delete_trip(id):
    """Delete a trip"""
    try:
        trip = Trip.query.get_or_404(id)
        role = _current_role()
        user_id = _current_user_id()

        if not _can_manage_trip(trip, role, user_id):
            flash('No tienes permisos para borrar este viaje.', 'error')
            return redirect(url_for('trip.view_trip', id=trip.idTrip))

        db.session.delete(trip)
        db.session.commit()
        
        flash('Trip deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting trip: {str(e)}', 'error')
    
    return redirect(url_for('trip.list_trips'))
