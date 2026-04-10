from flask import current_app as app , request, jsonify
from .models import *
from .database import db

from sqlalchemy import desc
from datetime import datetime

#1.login
@app.post('/api/login')
def api_login():
    data=request.json
    username=data.get('username')
    password=data.get('password')
    
    try:
        this_user=User.query.filter_by(username=username).first()
    
        if  this_user:
            if this_user.password==password:
                if this_user.type=='admin':
                    return jsonify(message='admin logged in successfully')
                else:
                    return jsonify(message='user logged successfully')
            else:
                return jsonify(message='Incorrect password'),400
        else:
            return jsonify(message='User not found with credential'),404
    
    except Exception as e:
        return jsonify(error='Internal server Error'),500


#2.register
@app.post('/api/register')
def api_register():
    data=request.json
    username = data.get("username")
    pwd = data.get("password")
    fullname = data.get("fullname")
    dob = data.get("dob")

    try:
        if User.query.filter_by(username=username).first():
            return jsonify(message="Username already exists"), 400
        user = User(username=username, password=pwd, fullname=fullname, dob=dob)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="Registration successful"), 201
    
    except Exception as e:
        return jsonify(error='Internal server Error'),500
    
#3. update user
@app.put("/api/update_user/<int:user_id>")
def api_update(user_id):
    try:
        this_user = User.query.get(user_id)
        if this_user:
            this_user.username = request.json.get("username")
            this_user.email = request.json.get("email")
            this_user.password = request.json.get("password")
            this_user.dob = request.json.get('dob')
            db.session.commit()
            return jsonify(message="user updated successfully"),200
        else:
            return jsonify(error="Incorrect user id"),400
    except Exception as e:
        return jsonify(error = "Internal server error"),500


#4. delete user
@app.delete("/api/delete_user/<int:user_id>")
def api_delete(user_id):
    try:
        this_user = User.query.get(user_id)
        if this_user:
            db.session.delete(this_user)
            db.session.commit()
            return jsonify(message ="user deleted successfully"),200
        else:
            return jsonify(error="Incorrect user id"),400
    except Exception as e:
        return jsonify(error= "Internal server error"),500
    

# 3. Parking lot list (GET) and create (POST)
@app.route("/api/parkinglots", methods=["GET", "POST"])
def api_parkinglots():
    try:
        if request.method == "GET":
            lots = ParkingLot.query.all()
            return jsonify([
                {
                    "id": lot.id,
                    "prime_location_name": lot.prime_location_name,
                    "address": lot.address,
                    "pin_code": lot.pin_code,
                    "price": lot.price,
                    "max_no_spots": lot.max_no_spots,
                    "available_spots": sum(spot.status == "A" for spot in lot.spots),
                }
                for lot in lots
            ])
        else:  # POST
            data = request.json
            lot = ParkingLot(
                prime_location_name=data.get("prime_location_name"),
                address=data.get("address"),
                pin_code=data.get("pin_code"),
                price=float(data.get("price")),
                max_no_spots=int(data.get("max_no_spots")),
            )
            db.session.add(lot)
            db.session.commit()
            for _ in range(lot.max_no_spots):
                db.session.add(ParkingSpot(lot_id=lot.id, status="A"))
            db.session.commit()
            return jsonify(message="Parking lot created"), 201
    except Exception as e:
        db.session.rollback()
        # print(e)
        return jsonify(error="Internal server error"), 500

# 4. Parking lot detail (GET, PUT, DELETE)
@app.route("/api/parkinglots/<int:lot_id>", methods=["GET", "PUT", "DELETE"])
def api_parkinglot_detail(lot_id):
    try:
        lot = ParkingLot.query.get_or_404(lot_id)
        if request.method == "GET":
            available = sum(spot.status == "A" for spot in lot.spots)
            return jsonify(
                {
                    "id": lot.id,
                    "prime_location_name": lot.prime_location_name,
                    "address": lot.address,
                    "pin_code": lot.pin_code,
                    "price": lot.price,
                    "max_no_spots": lot.max_no_spots,
                    "available_spots": available,
                }
            )
        elif request.method == "PUT":
            data = request.json
            lot.prime_location_name = data.get("prime_location_name", lot.prime_location_name)
            lot.address = data.get("address", lot.address)
            lot.pin_code = data.get("pin_code", lot.pin_code)
            lot.price = float(data.get("price", lot.price))
            new_max = int(data.get("max_no_spots", lot.max_no_spots))
            current_spots = len(lot.spots)
            if new_max > current_spots:
                for _ in range(new_max - current_spots):
                    db.session.add(ParkingSpot(lot_id=lot.id, status="A"))
            elif new_max < current_spots:
                free_spots = [spot for spot in lot.spots if spot.status == "A"]
                for _ in range(current_spots - new_max):
                    if free_spots:
                        db.session.delete(free_spots.pop())
            lot.max_no_spots = new_max
            db.session.commit()
            return jsonify(message="Lot updated")
        else:  # DELETE
            occupied_spots = [spot for spot in lot.spots if spot.status == "O"]
            if occupied_spots:
                return jsonify(message="Cannot delete lot with occupied spots. Free them first."), 400
            for spot in lot.spots:
                db.session.delete(spot)
            db.session.delete(lot)
            db.session.commit()
            return jsonify(message="Lot deleted")
    except Exception as e:
        db.session.rollback()
        # print(e)
        return jsonify(error="Internal server error"), 500

# 5. Spot List for parking lot
@app.route("/api/parkinglots/<int:lot_id>/spots", methods=["GET"])
def api_spots_list(lot_id):
    try:
        ParkingLot.query.get_or_404(lot_id)  # Ensures lot exists
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return jsonify([{"id": spot.id, "status": spot.status} for spot in spots])
    except Exception as e:
        # print(e)
        return jsonify(error="Internal server error"), 500


# 6. Reserve (book) a spot
@app.post("/api/reserve")
def api_reserve():
    try:
        data = request.json
        user_id = data.get("user_id")
        lot_id = data.get("lot_id")
        vehicle_no = data.get("vehicle_no")
        lot = ParkingLot.query.get_or_404(lot_id)
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status="A").first()
        if not available_spot:
            return jsonify(message="No spots available"), 400
        available_spot.status = "O"
        new_reserve = ReserveSpot(
            spot_id=available_spot.id,
            user_id=user_id,
            parking_timestamp=datetime.utcnow(),
            cost_per_hour=lot.price,
            vehicle_no=vehicle_no,
        )
        db.session.add(new_reserve)
        db.session.commit()
        return jsonify(
            message="Spot booked",
            reservation_id=new_reserve.id,
            spot_id=available_spot.id,
        ), 201
    except Exception as e:
        db.session.rollback()
        # print(e)
        return jsonify(error="Internal server error"), 500

# 7. Release spot
@app.post("/api/release")
def api_release():
    try:
        data = request.json
        reservation_id = data.get("reservation_id")
        reservation = ReserveSpot.query.get_or_404(reservation_id)
        if reservation.leaving_timestamp:
            return jsonify(message="Spot already released"), 400
        reservation.leaving_timestamp = datetime.utcnow()
        spot = ParkingSpot.query.get(reservation.spot_id)
        spot.status = "A"
        duration_hours = (
            (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds()
            / 3600.0
        )
        reservation.total_cost = duration_hours * reservation.cost_per_hour
        db.session.commit()
        return jsonify(
            message="Spot released",
            total_cost=round(reservation.total_cost, 2),
        )
    except Exception as e:
        db.session.rollback()
        # print(e)
        return jsonify(error="Internal server error"), 500

# 8. User reservations
@app.route("/api/user/<int:user_id>/reservations", methods=["GET"])
def api_user_reservations(user_id):
    try:
        reservations = (
            ReserveSpot.query.filter_by(user_id=user_id)
            .order_by(desc(ReserveSpot.parking_timestamp))
            .all()
        )
        result = []
        for r in reservations:
            spot = ParkingSpot.query.get(r.spot_id)
            lot = ParkingLot.query.get(spot.lot_id) if spot else None
            result.append(
                {
                    "reservation_id": r.id,
                    "vehicle_no": r.vehicle_no,
                    "parking_timestamp": r.parking_timestamp.isoformat() if r.parking_timestamp else None,
                    "leaving_timestamp": r.leaving_timestamp.isoformat() if r.leaving_timestamp else None,
                    "location": lot.prime_location_name if lot else None,
                    "total_cost": r.total_cost,
                }
            )
        return jsonify(result)
    except Exception as e:
        # print(e)
        return jsonify(error="Internal server error"), 500