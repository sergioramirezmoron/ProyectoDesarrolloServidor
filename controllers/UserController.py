from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

userBp = Blueprint('userBp', __name__)

class UserController:
    
    @staticmethod
    @userBp.route('/login', methods=['GET', 'POST'])
    def login():
        if 'userId' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                session['email'] = user.email
                session['userId'] = user.idUser
                session['role'] = user.role 
                return redirect(url_for('index'))
            
            return render_template('login.html', error="Invalid email or password")
                
        return render_template('login.html')

    @staticmethod
    @userBp.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'user') 
            
            if User.query.filter_by(email=email).first():
                return render_template('register.html', error="User already exists")
            
            hashedPassword = generate_password_hash(password)
            
            newUser = User(name=name, email=email, password=hashedPassword, role=role)
            
            db.session.add(newUser)
            db.session.commit()
            
            return redirect(url_for('userBp.login'))
            
        return render_template('register.html')

    @staticmethod
    @userBp.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('userBp.login'))