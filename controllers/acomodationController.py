from flask import Blueprint, render_template, flash, redirect, url_for, request, session, current_app
from models import User, Accommodation, db, AccommodationBookingLine, Room
import os
from werkzeug.utils import secure_filename

acomodation_bp = Blueprint('aco', __name__, template_folder='../templates')

# =========================
# ADMIN DASHBOARD
# =========================
@acomodation_bp.route('/admin/dashboard')
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin": # changed to admin lowercase
        flash('Permission denied')
        return redirect(url_for('aco.home'))
    
    users = User.query.all()
    accommodations = Accommodation.query.all()
    bookings = AccommodationBookingLine.query.order_by(AccommodationBookingLine.bookingDate.desc()).limit(20).all()
    
    return render_template('admin_dashboard.html', 
                           users_count=len(users),
                           accommodations_count=len(accommodations),
                           bookings_count=len(bookings), # Total logic might vary but sending list length for simple summary or separate query for count
                           accommodations=accommodations,
                           bookings=bookings)

# =========================
# MANAGE HOTELS (Company)
# =========================
@acomodation_bp.route('/manage_hotels')
def manage_hotels():
    if "user_id" not in session or session.get("role") != "company":
         flash('Access denied.')
         return redirect(url_for('userBp.login'))
         
    accommodations = Accommodation.query.filter_by(idCompany=session["user_id"]).all()
    return render_template('manage_hotels.html', accommodations=accommodations)


# =========================
# HOME (Landing Page)
# =========================
@acomodation_bp.route('/')
def home():
    accommodations = Accommodation.query.limit(9).all()
    return render_template('index.html', accommodations=accommodations)

# =========================
# SEARCH
# =========================
@acomodation_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('location', '')
    if query:
        results = Accommodation.query.filter(
            (Accommodation.name.ilike(f'%{query}%')) | 
            (Accommodation.address.ilike(f'%{query}%'))
        ).all()
    else:
        results = Accommodation.query.all()
    
    return render_template('index.html', accommodations=results)


# =========================
# CREATE
# =========================
@acomodation_bp.route('/acomodation/create', methods=['GET', 'POST'])
def create():

    if "user_id" not in session:
        flash('Debes iniciar sesión')
        return redirect(url_for('userBp.login'))

    if session.get("role") not in ["company", "admin"]:
        flash('No tienes permisos')
        return redirect(url_for('aco.home'))

    if request.method == 'POST':
        accommodation = Accommodation(
            name=request.form['name'],
            address=request.form['address'],
            phoneNumber=request.form['phoneNumber'],
            web=request.form['web'],
            stars_quality=request.form['stars_quality'],
            description=request.form['description'],
            type=request.form['type'],
            idCompany=session["user_id"]
        )

        # Handle Image Upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # Ensure the upload folder exists
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                accommodation.image = filename

        db.session.add(accommodation)
        db.session.commit()
        flash('Propiedad creada exitosamente', 'success')
        return redirect(url_for('aco.manage_hotels'))
    
    return render_template('acomodationCreate.html')


# =========================
# SHOW
# =========================
@acomodation_bp.route('/acomodation/show/<int:id>', methods=['GET'])
def show(id):
    accommodation = Accommodation.query.get_or_404(id)
    
    # Check if user can leave a review
    can_review = False
    if "user_id" in session:
        from models import AccommodationBookingLine, Review
        has_stayed = AccommodationBookingLine.query.filter_by(
            idUser=session["user_id"], 
            idAccommodation=id, 
            status='confirmed'
        ).first()
        
        # Optionally check if they already reviewed (to not show the button again)
        already_reviewed = Review.query.filter_by(
            idUser=session["user_id"],
            idAccommodation=id
        ).first()

        if has_stayed and not already_reviewed:
            can_review = True

    # Get dates from query params if available
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    
    # If dates are provided, filter or flag rooms based on availability
    rooms_data = []
    if checkin and checkout:
        try:
            start_date = datetime.strptime(checkin, '%Y-%m-%d').date()
            end_date = datetime.strptime(checkout, '%Y-%m-%d').date()
            for room in accommodation.rooms:
                is_available = room.is_available(start_date, end_date)
                rooms_data.append({
                    'room': room,
                    'is_available': is_available
                })
        except ValueError:
            # If dates are invalid, just show all as available
            rooms_data = [{'room': r, 'is_available': True} for r in accommodation.rooms]
    else:
        rooms_data = [{'room': r, 'is_available': True} for r in accommodation.rooms]
    
    return render_template('acomodationShow.html', 
                           accommodation=accommodation, 
                           rooms_data=rooms_data,
                           checkin=checkin, 
                           checkout=checkout,
                           can_review=can_review)


# =========================
# DELETE
# =========================
@acomodation_bp.route('/acomodation/delete/<int:id>', methods=['POST'])
def delete(id):

    if "user_id" not in session:
        flash('Debes iniciar sesión')
        return redirect(url_for('userBp.login'))

    accommodation = Accommodation.query.get_or_404(id)

    if session["user_id"] != accommodation.idCompany and session.get("role") != "admin":
        flash('No tienes permiso')
        return redirect(url_for('aco.home'))

    db.session.delete(accommodation)
    db.session.commit()
    return redirect(url_for('aco.home'))


# =========================
# EDIT
# =========================
@acomodation_bp.route('/acomodation/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    if "user_id" not in session:
        flash('Debes iniciar sesión')
        return redirect(url_for('userBp.login'))

    accommodation = Accommodation.query.get_or_404(id)

    if session["user_id"] != accommodation.idCompany and session.get("role") != "admin": # changed ADMIN to admin
        flash('No tienes permiso')
        return redirect(url_for('aco.home'))

    if request.method == 'POST':
        accommodation.name = request.form['name']
        accommodation.address = request.form['address']
        accommodation.phoneNumber = request.form['phoneNumber']
        accommodation.web = request.form['web']
        accommodation.stars_quality = request.form['stars_quality']
        accommodation.description = request.form['description']
        accommodation.type = request.form['type']

        # Handle Image Upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                os.makedirs(current_app.app_context().app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(current_app.app_context().app.config['UPLOAD_FOLDER'], filename))
                accommodation.image = filename

        db.session.commit()
        return redirect(url_for('aco.home'))
        
    return render_template('acomodationEdit.html', accommodation=accommodation)

# =========================
# MANAGE ROOMS
# =========================
@acomodation_bp.route('/acomodation/<int:id>/rooms', methods=['GET'])
def manage_rooms(id):
    if "user_id" not in session:
        return redirect(url_for('userBp.login'))
        
    accommodation = Accommodation.query.get_or_404(id)
    
    # Check ownership or admin
    if session["user_id"] != accommodation.idCompany and session.get("role") != "admin": # changed ADMIN to admin (lowercase based on User model default)
        flash('Permission denied')
        return redirect(url_for('aco.home'))

    return render_template('manage_rooms.html', accommodation=accommodation)

@acomodation_bp.route('/acomodation/<int:id>/rooms/add', methods=['POST'])
def add_room(id):
    if "user_id" not in session:
        return redirect(url_for('userBp.login'))
        
    accommodation = Accommodation.query.get_or_404(id)
    
    if session["user_id"] != accommodation.idCompany and session.get("role") != "admin":
        flash('Permission denied')
        return redirect(url_for('aco.home'))
    
    new_room = Room(
        idAccommodation=id,
        roomNumber=request.form['roomNumber'],
        type=request.form['type'],
        priceNight=request.form['priceNight'],
        capacity=request.form['capacity']
    )
    
    db.session.add(new_room)
    db.session.commit()
    
    flash('Room added successfully!')
    return redirect(url_for('aco.manage_rooms', id=id))

@acomodation_bp.route('/acomodation/rooms/delete/<int:id>', methods=['POST'])
def delete_room(id):
    if "user_id" not in session:
        return redirect(url_for('userBp.login'))
        
    # Corrected import
    room = Room.query.get_or_404(id)
    accommodation = Accommodation.query.get(room.idAccommodation)
    
    if session["user_id"] != accommodation.idCompany and session.get("role") != "admin":
        flash('Permission denied')
        return redirect(url_for('aco.home'))
        
    db.session.delete(room)
    db.session.commit()
    
    flash('Room deleted successfully!')
    return redirect(url_for('aco.manage_rooms', id=accommodation.id))
