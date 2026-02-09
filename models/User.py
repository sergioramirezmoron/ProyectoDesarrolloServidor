from .db import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)

    @property
    def isAdmin(self):
        return self.role == 'admin'

    @property
    def isUser(self):
        return self.role == 'user'
    
    @property 
    def isCompany(self):
        return self.role == 'company'
