from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Location

location_bp = Blueprint('location', __name__, template_folder='../templates')

@location_bp.route('/create', methods=['GET', 'POST'])
def create():
    if "user_id" not in session or session.get("role") != "admin":
        flash('Permission denied', 'danger')
        return redirect(url_for('aco.home'))

    if request.method == 'POST':
        country = request.form.get('country')
        city = request.form.get('city')

        if not country or not city:
            flash('Country and City are required.', 'warning')
            return render_template('createLocationForm.html')

        new_location = Location(country=country, city=city)
        db.session.add(new_location)
        db.session.commit()
        
        flash('Location created successfully!', 'success')
        return redirect(url_for('aco.admin_dashboard'))

    return render_template('createLocationForm.html')
