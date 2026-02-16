from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from models.db import db
from equipo3.models.Accommodation import Accommodation
from equipo3.models.AccommodationBookingLine import AccommodationBookingLine
from equipo3.models.Review import Review
from equipo3.models.Room import Room
from models.User import User
from datetime import datetime

booking_bp = Blueprint('booking', __name__, template_folder='../templates')

# =========================
# COMPANY BOOKINGS
# =========================
@booking_bp.route('/company/bookings', methods=['GET'])
def company_bookings():
    if "user_id" not in session or session.get("role") != "company":
        return redirect(url_for('login'))

    # Fetch accommodations owned by the company
    company_accommodations = Accommodation.query.filter_by(idCompany=session["user_id"]).with_entities(Accommodation.id).all()
    accommodation_ids = [acc.id for acc in company_accommodations]

    # Fetch bookings for these accommodations
    bookings = AccommodationBookingLine.query.filter(AccommodationBookingLine.idAccommodation.in_(accommodation_ids)).order_by(AccommodationBookingLine.startDate.desc()).all()

    return render_template('companyBookings.html', bookings=bookings)


# =========================
# CANCEL BOOKING
# =========================
@booking_bp.route('/booking/cancel/<int:id>', methods=['POST'])
def cancel_booking(id):
    if "user_id" not in session:
        return redirect(url_for('login'))

    booking = AccommodationBookingLine.query.get_or_404(id)
    accommodation = Accommodation.query.get(booking.idAccommodation)

    # Allow cancellation if user owns the booking OR user owns the property OR user is admin
    is_owner = booking.idUser == session["user_id"]
    is_host = accommodation.idCompany == session["user_id"]
    is_admin = session.get("role") == "admin" # changed to admin lowercase

    if not (is_owner or is_host or is_admin):
        flash('Permission denied')
        return redirect(url_for('aco.home'))

    booking.status = 'cancelled'
    db.session.commit()
    
    flash('Booking cancelled successfully')
    
    # Redirect back to where they came from (conceptually)
    if is_host:
        return redirect(url_for('booking.company_bookings'))
    elif is_admin:
        return redirect(url_for('aco.admin_dashboard')) # Placeholder for now
    else:
        return redirect(url_for('booking.list_user_bookings_html', user_id=session["user_id"]))

# =========================
# FORMULARIO RESERVA
# =========================
@booking_bp.route('/book', methods=['GET', 'POST'])
def book_accommodation():
    if request.method == 'POST':
        user_id = request.form.get('userId')
        accommodation_id = request.form.get('accommodationId')
        room_id = request.form.get('roomId') # Added roomId
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')
        total_price = request.form.get('totalPrice')

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            if start_date > end_date:
                return render_template('book.html', error='La fecha de inicio no puede ser posterior a la fecha de fin.')

            booking = AccommodationBookingLine(
                idUser=user_id,
                idAccommodation=accommodation_id,
                idRoom=room_id, # Added idRoom
                startDate=start_date,
                endDate=end_date,
                totalPrice=total_price,
                status='pending'
            )

            db.session.add(booking)
            db.session.commit()
            return redirect(url_for('accommodation.list_user_bookings_html', user_id=user_id))

        except Exception as e:
            db.session.rollback()
            return render_template('book.html', error=str(e))

    accommodations = Accommodation.query.all()
    users = User.query.all()
    return render_template('book.html', accommodations=accommodations, users=users)


# =========================
# FORMULARIO RESEÑA
# =========================
@booking_bp.route('/review', methods=['GET', 'POST'])
def add_review():
    if request.method == 'POST':
        user_id = request.form.get('idUser')
        accommodation_id = request.form.get('idAccommodation')
        rating = request.form.get('ratingStars')
        comment = request.form.get('reviewComment')

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return render_template('review.html', error='La calificación debe estar entre 1 y 5.')

            review = Review(
                idUser=user_id,
                idAccommodation=accommodation_id,
                ratingStars=rating,
                reviewComment=comment
            )
            db.session.add(review)
            db.session.commit()
            return redirect(url_for('accommodation.list_accommodation_reviews_html', accommodation_id=accommodation_id))

        except Exception as e:
            db.session.rollback()
            return render_template('review.html', error=str(e))

    accommodations = Accommodation.query.all()
    users = User.query.all()
    return render_template('review.html', accommodations=accommodations, users=users)


# =========================
# LISTAR RESERVAS (JSON)
# =========================
@booking_bp.route('/bookings/json/<int:user_id>', methods=['GET'])
def list_user_bookings(user_id):
    bookings = AccommodationBookingLine.query.filter_by(idUser=user_id).all()
    return jsonify([{
        'id': b.id,
        'accommodationId': b.idAccommodation,
        'startDate': b.startDate.isoformat(),
        'endDate': b.endDate.isoformat(),
        'totalPrice': float(b.totalPrice),
        'status': b.status
    } for b in bookings])


# =========================
# LISTAR RESERVAS (HTML)
# =========================
@booking_bp.route('/bookings/<int:user_id>', methods=['GET'])
def list_user_bookings_html(user_id):
    bookings = AccommodationBookingLine.query.filter_by(idUser=user_id).all()
    return render_template('bookings.html', bookings=bookings)


# =========================
# LISTAR RESEÑAS (JSON)
# =========================
@booking_bp.route('/reviews/json/<int:accommodation_id>', methods=['GET'])
def list_accommodation_reviews(accommodation_id):
    reviews = Review.query.filter_by(idAccommodation=accommodation_id).all()
    return jsonify([{
        'idReview': r.id,
        'idUser': r.idUser,
        'ratingStars': r.ratingStars,
        'reviewComment': r.reviewComment,
        'createdAt': r.createdAt.isoformat()
    } for r in reviews])


# =========================
# LISTAR RESEÑAS (HTML)
# =========================
@booking_bp.route('/reviews/<int:accommodation_id>', methods=['GET'])
def list_accommodation_reviews_html(accommodation_id):
    reviews = Review.query.filter_by(idAccommodation=accommodation_id).all()
    return render_template('reviews.html', reviews=reviews)