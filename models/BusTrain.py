from .db import db

class BusTrain(db.Model):
    __tablename__ = 'bus_train'
    idBusTrain = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('bus', 'train'), nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    idCompany = db.Column(db.Integer, db.ForeignKey('user.idUser'), nullable=False)
    idLocationStart = db.Column(db.Integer, db.ForeignKey('location.idLocation'), nullable=False)
    idLocationEnd = db.Column(db.Integer, db.ForeignKey('location.idLocation'), nullable=False)
    company = db.relationship('User', foreign_keys=[idCompany])
    locationStart = db.relationship('Location', foreign_keys=[idLocationStart])
    locationEnd = db.relationship('Location', foreign_keys=[idLocationEnd])

    def toDict(self):
        return {
            "idBusTrain": self.idBusTrain,
            "type": self.type,
            "startDate": self.startDate.strftime('%Y/%m/%d %H:%M:%S'),
            "endDate": self.endDate.strftime('%Y/%m/%d %H:%M:%S'),
            "price": self.price,
            "idCompany": self.idCompany,
            "idLocationStart": self.idLocationStart,
            "idLocationEnd": self.idLocationEnd
        }