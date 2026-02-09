from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

class UserController:
    
    @staticmethod
    def login():
        if 'userId' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                session['email'] = user.email
                session['userId'] = user.id
                session['role'] = user.role 
                session['isAdmin'] = user.isAdmin
                
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Invalid email or password")
                
        return render_template('login.html')

    @staticmethod
    def register():
        if 'userId' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                return render_template('register.html', error="User with this email already exists")
            
            hashedPassword = generate_password_hash(password)
            
            newUser = User(name=name, email=email, password=hashedPassword)
            
            db.session.add(newUser)
            db.session.commit()
            
            return redirect(url_for('login'))
            
        return render_template('register.html')

    @staticmethod
    def logout():
        session.clear()
        return redirect(url_for('login'))