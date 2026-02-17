from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Trip, Location, User
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
        'trip/trip_list.html',
        trips=trips,
        user_role=role,
        current_user_id=user_id,
    )

@trip_bp.route('/<int:id>')
def view_trip(id):
    """View trip details"""
    trip = Trip.query.get_or_404(id)
    role = _current_role()
    user_id = _current_user_id()
    return render_template(
        'trip/trip_detail.html',
        trip=trip,
        user_role=role,
        current_user_id=user_id,
    )
