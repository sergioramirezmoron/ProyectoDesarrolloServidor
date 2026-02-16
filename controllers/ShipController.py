from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db
from models.Cruise import Ship
from models.User import User

ship_bp = Blueprint('ship', __name__, url_prefix='/ships')

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

@ship_bp.route('/', methods=['GET'])
def my_ships():
    user = get_current_user()
    if not user or user.role != 'company':
        flash('Solo las compañías pueden gestionar barcos.')
        return redirect(url_for('index'))
    ships = Ship.query.filter_by(idCompany=user.idUser).all()
    return render_template('my_ships.html', ships=ships, user=user)

@ship_bp.route('/create', methods=['GET', 'POST'])
def create_ship():
    user = get_current_user()
    if not user or user.role != 'company':
        flash('Solo las compañías pueden crear barcos.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        cruiseName = request.form['cruiseName']
        capacity = int(request.form['capacity'])
        ship = Ship(idCompany=user.idUser, cruiseName=cruiseName, capacity=capacity)
        db.session.add(ship)
        db.session.commit()
        flash('¡Barco creado!')
        return redirect(url_for('ship.my_ships'))
    return render_template('ship_form.html', user=user)
