from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Location

location_bp = Blueprint('location', __name__, template_folder='../templates')

@location_bp.route('/list', methods=['GET'])
def index():
    if "user_id" not in session or session.get("role") != "admin":
        flash('Permission denied', 'danger')
        return redirect(url_for('aco.home'))
    
    locations = Location.query.all()
    return render_template('location_list.html', locations=locations)

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
            return render_template('location_form.html', action="Crear")

        new_location = Location(country=country, city=city)
        db.session.add(new_location)
        db.session.commit()
        
        flash('Localización creada exitosamente.', 'success')
        return redirect(url_for('location.index'))

    return render_template('location_form.html', action="Crear")

@location_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if "user_id" not in session or session.get("role") != "admin":
        flash('Permission denied', 'danger')
        return redirect(url_for('aco.home'))
    
    location = Location.query.get_or_404(id)

    if request.method == 'POST':
        country = request.form.get('country')
        city = request.form.get('city')

        if not country or not city:
            flash('Country and City are required.', 'warning')
            return render_template('location_form.html', location=location, action="Editar")

        location.country = country
        location.city = city
        db.session.commit()
        
        flash('Localización actualizada exitosamente.', 'success')
        return redirect(url_for('location.index'))

    return render_template('location_form.html', location=location, action="Editar")

@location_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if "user_id" not in session or session.get("role") != "admin":
        flash('Permission denied', 'danger')
        return redirect(url_for('aco.home'))
    
    location = Location.query.get_or_404(id)
    try:
        db.session.delete(location)
        db.session.commit()
        flash('Localización eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('No se puede eliminar la localización porque está en uso.', 'danger')
        
    return redirect(url_for('location.index'))
