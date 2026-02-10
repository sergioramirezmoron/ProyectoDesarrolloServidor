from .db import db

class User(db.Model):
    __tablename__ = 'user'
    idUser = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'admin', 'company'), default='user', nullable=False)

    @property
    def isAdmin(self):
        return self.role == 'admin'

    @property
    def isUser(self):
        return self.role == 'user'
    
    @property 
    def isCompany(self):
        return self.role == 'company'

    def toDict(self):
        return {
            "idUser": self.idUser,
            "name": self.name,
            "email": self.email,
            "role": self.role
        }