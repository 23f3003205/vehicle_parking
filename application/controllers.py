from flask import Flask , render_template ,redirect ,request,url_for,session,flash
from flask import current_app as app  #it refers to app object created , 
from sqlalchemy import desc , func   # for ordering

from datetime import datetime

import pytz
IST = pytz.timezone('Asia/Kolkata')

from .models import * # . dot refers that search models.py in existing folder

@app.route("/create-admin")
def create_admin():
    user = User(username="admin123", password="1234", fullname="Admin", type="admin")
    db.session.add(user)
    db.session.commit()
    return "Admin created"

@app.route("/add-dum-user")
def create_user():
    user = User(username="harsh123", password="1234", fullname="harsh",dob="15-04-2204")
    db.session.add(user)
    db.session.commit()
    return "User created"


@app.route('/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        pwd=request.form.get('password')
        this_user=User.query.filter_by(username=username).first()

        if this_user :
            if this_user.password == pwd:
                session['user_id']=this_user.id # store user id in session
                session['type']=this_user.type   # is visitor user or admin

                if this_user.type=='admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('password is incorrect','danger') 

        else:
            flash('user not found , register first and may be password incorrect','warning') 
            
    return render_template('auth/login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        pwd=request.form.get('password')
        fullname=request.form.get('fullname')
        dob=request.form.get('dob')

        if User.query.filter_by(username=username).first():
            return ' username already exist'
        else:
            new_user=User(username=username,password=pwd,fullname=fullname,dob=dob)
            db.session.add(new_user)
            db.session.commit()
            
            return redirect(url_for('login'))

    return render_template('auth/register.html')

@app.route('/admin_dashboard',methods=['GET','POST'])
def admin_dashboard():
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
    parking_lots=ParkingLot.query.all()
    for lot in parking_lots:
        lot.occupied_count=sum(spot.status == 'O' for spot in lot.spots )
    
    return render_template('admin/admin_dashboard.html',parking_lots=parking_lots)


@app.route('/admin_dashboard/registered_users' )
def registered_users():
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
    users=User.query.filter(User.type != 'admin').all()
    
    return render_template('admin/register_user_detail.html',users=users)

@app.route('/admin_dashboard/summary')
def admin_summary():
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))

    # Total earnings per parking lot
    earnings = (
        db.session.query(ParkingLot.prime_location_name, func.sum(ReserveSpot.total_cost))
        .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)
        .join(ReserveSpot, ReserveSpot.spot_id == ParkingSpot.id)
        .group_by(ParkingLot.prime_location_name)
        .all()
    )

    labels = [lot for lot, _ in earnings]
    values = [round(total or 0, 2) for _, total in earnings]

    return render_template('admin/summary_chart.html', labels=labels, values=values)
    



@app.route('/admin_dashboard/search',methods=['GET','POST'])
def admin_search():
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
     # Initialize variables for template

    register_user_detail=None
    requested_lot_detail=None
    search_query=None

    if request.method=='POST':
        search_by=request.form.get('search_by')
        search_value=request.form.get('search_value','').strip()

        if search_by == 'user_id':
            if search_value.isdigit():
                register_user_detail = User.query.filter_by(id=int(search_value)).first()
                if register_user_detail:
                    search_query = f'user id {search_value}'
                else:
                    flash('Invalid User Id', 'danger')
            else:
                flash('User Id must be a number', 'danger')

        elif search_by == 'prime_location_name':
            requested_lot_detail = ParkingLot.query.filter_by(prime_location_name=search_value).first()
            if requested_lot_detail:
                requested_lot_detail.occupied_count = sum(spot.status == 'O' for spot in requested_lot_detail.spots)
                search_query = f'prime location {search_value}'
            else:
                flash('Invalid prime location name', 'danger')


    
    return render_template('admin/admin_search_page.html',register_user_detail=register_user_detail,lot=requested_lot_detail,search_query=search_query) # Pass the filtered users
   

@app.route('/admin_dashboard/edit_lot/<int:lot_id>', methods=['GET','POST'])
def edit_lot(lot_id):
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
    lot=ParkingLot.query.get(lot_id)

    if request.method=='POST':
        new_max_no_spots=int(request.form['max_no_spots'])  # get the no. of spots to be update

        # calcualte the currently occupied spots
        occupied_spots_count=sum(1 for spot in lot.spots if spot.status == "O")

        if new_max_no_spots < occupied_spots_count : 
            # ERROR message
            flash(f" cannot decrease spots below currently occupieds spots number {occupied_spots_count} , Please free up spots first",'danger')
            return redirect(url_for('edit_lot',lot_id=lot.id)) #redirect to back to editlot

        lot.prime_location_name=request.form['location']
        lot.address=request.form['address']
        lot.pin_code=request.form['pincode']
        lot.price=request.form['price']

        #update max no spots 
        lot.max_no_spots=new_max_no_spots

        #Handling increasing or decreasing stocks
        current_spot_counts=len(lot.spots)

        if new_max_no_spots > current_spot_counts:
            # ADd new spots if max_no_spots increased

            spots_to_add=new_max_no_spots-current_spot_counts
            for i in range(spots_to_add):
                spot=ParkingSpot(lot_id=lot.id,status='A')
                db.session.add(spot)
        
        elif new_max_no_spots <  current_spot_counts :
            # remove available spots in max_spots decreased

            available_spots=[spot for spot in lot.spots if spot.status == 'A']
            spots_to_remove=current_spot_counts-new_max_no_spots

            for i in range(spots_to_remove):
                if available_spots:
                    spot_to_delete=available_spots.pop()
                    db.session.delete(spot_to_delete)
                else:
                    break


        db.session.commit()
        flash('parking lot update successfully','success')  #Flash success message
        return redirect(url_for('admin_dashboard'))

    
    return render_template('admin/edit_parking_lot.html',lot=lot)

@app.route('/admin_dashboard/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))

    lot=ParkingLot.query.get(lot_id)
    
    # Check if the lot exists
    if not lot:
        flash("Parking lot not found.", 'danger')
        return redirect(url_for('admin_dashboard'))

    # Check for occupied spots
    occupied_spots_count = sum(1 for spot in lot.spots if spot.status == 'O')
    
    if occupied_spots_count > 0:
        flash(f"Cannot delete lot '{lot.prime_location_name}' as it has {occupied_spots_count} occupied spots. Please ensure all spots are empty before deleting the lot.", 'danger')
        return redirect(url_for('admin_dashboard'))
        
    # If no occupied spots, proceed with deletion
    for spot in lot.spots:
        db.session.delete(spot)
    db.session.delete(lot)
    db.session.commit()
    flash(f'Parking Lot {lot.prime_location_name} deleted successfully and its spots also','success')
    return redirect(url_for('admin_dashboard'))
    
@app.route('/admin_dashboard/spot_detail/<int:spot_id>' , methods=['GET','POST'])
def view_spot_detail(spot_id):
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
    spot= ParkingSpot.query.get(spot_id)
    if request.method=='POST':
        if spot.status == 'A':
            lot=ParkingLot.query.get(spot.lot_id)
            db.session.delete(spot)
            lot.max_no_spots-=1  # decrement spot count
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/view_del_spot.html',spot=spot)

@app.route("/admin_dashboard/spot_detail/occupied_spot_detail/<int:spot_id>",methods=['GET','POST'])
def occupied_spot_detail(spot_id):
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
    reservation_detail=ReserveSpot.query.filter_by(spot_id=spot_id).first()

    


    return render_template('admin/occupied_spot_detail.html',reservation=reservation_detail)

@app.route('/admin_dashboard/add_lot',methods=['GET','POST'])
def add_lot():
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        location=request.form['location']
        address=request.form['address']
        pincode=request.form['pincode']
        price=request.form['price']
        max_no_spots=int(request.form['number_of_spots'])

        new_lot=ParkingLot(prime_location_name=location,
            address=address,
            pin_code=pincode,
            price=price,
            max_no_spots=max_no_spots)
        
        db.session.add(new_lot)
        db.session.commit()

        for _ in range(max_no_spots):
            spot=ParkingSpot(lot_id=new_lot.id,status='A')
            db.session.add(spot)
        db.session.commit()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_parking_lot.html')
        

@app.route('/user_dashboard',methods=['GET','POST'])
def user_dashboard():
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
    #for fetching parking history of the user we need join reserve spot with Parking spot and Parking lot to get location_name
    recent_reserves=db.session.query(ReserveSpot,ParkingSpot,ParkingLot).join(ParkingSpot ,ReserveSpot.spot_id==ParkingSpot.id).join(ParkingLot,ParkingSpot.lot_id==ParkingLot.id).filter(ReserveSpot.user_id==user_id).order_by(desc(ReserveSpot.parking_timestamp)).all()

    # --- BEGIN: Convert timestamps to IST ---
    for res_tpl in recent_reserves:
        reservation = res_tpl[0]
        if reservation.parking_timestamp:
            reservation.parking_timestamp_ist = reservation.parking_timestamp.replace(tzinfo=pytz.UTC).astimezone(IST)
        else:
            reservation.parking_timestamp_ist = None

        if reservation.leaving_timestamp:
            reservation.leaving_timestamp_ist = reservation.leaving_timestamp.replace(tzinfo=pytz.UTC).astimezone(IST)
        else:
            reservation.leaving_timestamp_ist = None
    # --- END ---

    #Initialize Query for all parking spots
    parking_lots_query=ParkingLot.query
    search_query=None # To store the search term for displaying in the heading 

    if request.method == 'POST':
        search_by=request.form.get('search_by')
        search_value=request.form.get('search_value').strip()   

        if search_value:
            search_query=search_value
            if search_by == 'location' :
                parking_lots_query=parking_lots_query.filter(ParkingLot.prime_location_name.ilike(f'%{search_value}%'))
            elif search_by =='pincode':
                parking_lots_query=parking_lots_query.filter(ParkingLot.pin_code.ilike(f'%{search_value}%'))

            else:
                flash('Invalid Search Area Selected','warning')

            

    all_parking_lots_raw=parking_lots_query.all()
    # calculating available parking spots for each parking lot 
    parking_lots_with_availability = []
    for lot in all_parking_lots_raw:
        available_spots_count = sum(1 for spot in lot.spots if spot.status == 'A')
        parking_lots_with_availability.append({
            'id': lot.id,
            'prime_location_name': lot.prime_location_name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'price': lot.price,
            'max_no_spots': lot.max_no_spots,
            'available_spots': available_spots_count # Pre-calculated availability
        })


    #calculating available parking spots for each parking lot 
    
        
    fullname=user.fullname
    return render_template('user/user_dashboard.html',recent_reserves=recent_reserves,all_parking_lots=parking_lots_with_availability,fullname=fullname,search_query=search_query)


@app.route('/user_dashboard/release_spot/<int:reservation_id>',methods=['GET','POST'])
def release_spot(reservation_id):
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user_id or not user:
        return redirect(url_for('login'))

    reservation = ReserveSpot.query.get(reservation_id)

    if not reservation or reservation.user_id != user_id:
        flash("Reservation not found or you don't have permission.", 'danger')
        return redirect(url_for('user_dashboard'))
    if reservation.leaving_timestamp:
            flash("This spot has already been released.", 'warning')
            return redirect(url_for('user_dashboard'))

        # Update leaving timestamp
    leaving_timestamp = datetime.utcnow()
    leaving_timestamp_ist = leaving_timestamp.replace(tzinfo=pytz.UTC).astimezone(IST)
    
    if request.method=='POST':

        

        # Update parking spot status to 'Available'
        spot = ParkingSpot.query.get(reservation.spot_id)
        if spot:
            spot.status = 'A'

        reservation.leaving_timestamp=datetime.utcnow()
            
        # Calculate duration and cost
        duration_seconds = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds()
        duration_hours = duration_seconds / 3600
        total_cost = duration_hours * reservation.cost_per_hour
        reservation.total_cost = total_cost

        
        db.session.commit()
        flash(f"Spot successfully released! Total cost for reservation {reservation.id}: Rs. {total_cost:.2f}", 'success')
        return redirect(url_for('user_dashboard'))


    return render_template('user/release_parking_spot.html',reservation=reservation,leaving_timestamp=leaving_timestamp_ist)

@app.route('/user_dashboard/book_slot/<int:lot_id>',methods=['GET','POST'])
def book_spot(lot_id):
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))

    parking_lot=ParkingLot.query.get(lot_id)
    if not parking_lot:
        flash('Parking lot not found','danger') 
        return redirect(url_for('user_dashboard'))
    
    #find available spots in this lot 
    available_spot=ParkingSpot.query.filter(ParkingSpot.lot_id==lot_id,ParkingSpot.status=='A').first()
    
    if not available_spot:
        flash('spots not available for the lot','warning')
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        vehicle_no=request.form.get('vehicleNo','').strip()
        available_spot.status='O'
        #creating new reservation
        new_reservation=ReserveSpot(spot_id=available_spot.id,user_id=user_id,parking_timestamp=datetime.utcnow(),cost_per_hour=parking_lot.price,vehicle_no=vehicle_no)
        db.session.add(new_reservation)
        db.session.commit()
        flash('successfully booked spot','success')
        return redirect(url_for('user_dashboard'))

  
    return render_template('user/book_parking_spot.html',user_id=user_id,available_spot=available_spot)





@app.route('/user_summary',methods=['GET','POST'])
def user_summary():
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    
    if not user_id or not user:         #unauthenticated visit
        return redirect(url_for('login'))
    
    fullname=user.fullname

     # Daily cost data
    user_costs = db.session.query(
        func.date(ReserveSpot.parking_timestamp),
        func.sum(ReserveSpot.total_cost)
    ).filter(
        ReserveSpot.user_id == user_id
    ).group_by(
        func.date(ReserveSpot.parking_timestamp)
    ).order_by(
        func.date(ReserveSpot.parking_timestamp)
    ).all()

    labels = [date for date, _ in user_costs]
    values = [round(total or 0, 2) for _, total in user_costs]

    # Summary stats
    total_bookings = ReserveSpot.query.filter_by(user_id=user_id).count()
    total_cost = db.session.query(func.sum(ReserveSpot.total_cost)).filter_by(user_id=user_id).scalar() or 0
    avg_cost = db.session.query(func.avg(ReserveSpot.total_cost)).filter_by(user_id=user_id).scalar() or 0


    # Location-wise pie chart data
    location_data = db.session.query(
        ParkingLot.prime_location_name,
        func.count(ReserveSpot.id)
    ).join(ParkingSpot, ParkingSpot.id == ReserveSpot.spot_id
    ).join(ParkingLot, ParkingLot.id == ParkingSpot.lot_id
    ).filter(
        ReserveSpot.user_id == user_id
    ).group_by(
        ParkingLot.prime_location_name
    ).all()

    location_labels = [loc for loc, _ in location_data]
    location_counts = [count for _, count in location_data]

    return render_template('user/user_summary.html',
                           fullname=fullname,
                           labels=labels,
                           values=values,
                           total_bookings=total_bookings,
                           total_cost=round(total_cost, 2),
                           avg_cost=round(avg_cost, 2),
                           location_labels=location_labels,
                           location_counts=location_counts)
    
  
@app.route('/logout')
def logout():
    session.clear()
    return redirect( url_for('login'))




