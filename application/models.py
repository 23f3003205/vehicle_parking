from .database import db        # (.) "dot" tells check this file the folder you are residing
from datetime import datetime

class User(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(),unique=True,nullable=False)
    password=db.Column(db.String(),nullable=False)
    fullname=db.Column(db.String(),nullable=False)
    dob=db.Column(db.String(),nullable=True)
    type=db.Column(db.String(),default='general') # type can be user or admin 

    reservations=db.relationship('ReserveSpot',backref='user')

class ParkingLot(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    prime_location_name=db.Column(db.String(),nullable=False)
    price=db.Column(db.Float(),nullable=False)
    address=db.Column(db.String(),nullable=False)
    pin_code=db.Column(db.String(),nullable=False)
    max_no_spots=db.Column(db.Integer(),nullable=False)
    
    spots=db.relationship('ParkingSpot', backref='parking_lot')


class ParkingSpot(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    lot_id=db.Column(db.Integer(),db.ForeignKey('parking_lot.id'),nullable=False)
    status=db.Column(db.String(),default='A')  # A is available and O is occupied

    reservations=db.relationship('ReserveSpot' , backref='parking_spot')


class ReserveSpot(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    spot_id=db.Column(db.Integer(),db.ForeignKey('parking_spot.id'),nullable=False)
    user_id=db.Column(db.Integer(),db.ForeignKey('user.id'),nullable=False)
    vehicle_no=db.Column(db.String(),nullable=False)
    parking_timestamp=db.Column(db.DateTime,default=datetime.utcnow)
    leaving_timestamp=db.Column(db.DateTime,nullable=True)
    cost_per_hour=db.Column(db.Float(),nullable=False)
    total_cost = db.Column(db.Float(), nullable=True)  



