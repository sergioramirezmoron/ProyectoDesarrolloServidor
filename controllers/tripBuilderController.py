# controllers/tripBuilderController.py
# Trip Builder - Multi-step wizard for creating custom trips

from datetime import datetime
from decimal import Decimal
import json

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, UserTrip, TripItem
from models import Accommodation, Flight, Cruise, Car, Tour, BusTrain

tripBuilderBlueprint = Blueprint("tripBuilder", __name__, url_prefix="/trip-builder", template_folder="../templates/tripBuilder")

@tripBuilderBlueprint.app_template_filter('from_json')
def from_json_filter(value):
    return json.loads(value) if value else {}

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    from models import User
    return User.query.get(user_id)


def init_trip_session():
    """Initialize trip building session"""
    if 'trip_builder' not in session:
        session['trip_builder'] = {
            'trip_name': '',
            'start_date': None,
            'end_date': None,
            'items': []  # List of {type, id, price, details}
        }


def clear_trip_session():
    """Clear trip building session"""
    if 'trip_builder' in session:
        session.pop('trip_builder')


# ===== WIZARD FLOW =====

@tripBuilderBlueprint.route("/start", methods=["GET"])
def start():
    """Start the trip builder wizard"""
    user = get_current_user()
    if not user:
        flash("Debes iniciar sesión para crear un viaje.", "warning")
        return redirect(url_for("userBp.login"))
    
    if user.role != "user":
        flash("Solo los usuarios pueden crear viajes personalizados.", "warning")
        return redirect(url_for("aco.home"))
    
    # Clear any existing session
    clear_trip_session()
    init_trip_session()
    
    return render_template("tripBuilder/start.html", user=user)


@tripBuilderBlueprint.route("/start", methods=["POST"])
def save_trip_name():
    """Save trip name and proceed to first step"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    trip_name = request.form.get("trip_name", "Mi Viaje").strip()
    start_date = request.form.get("startDate")
    end_date = request.form.get("endDate")
    
    if not trip_name:
        trip_name = f"Viaje {datetime.now().strftime('%d/%m/%Y')}"
    
    init_trip_session()
    session['trip_builder']['trip_name'] = trip_name
    session['trip_builder']['start_date'] = start_date
    session['trip_builder']['end_date'] = end_date
    session.modified = True
    
    return redirect(url_for("tripBuilder.step_accommodation"))


# ===== STEP 1: ACCOMMODATION =====

@tripBuilderBlueprint.route("/step/accommodation", methods=["GET"])
def step_accommodation():
    """Step 1: Select accommodation"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    trip_data = session['trip_builder']
    start_date = trip_data.get('start_date')
    end_date = trip_data.get('end_date')
    
    # Query for accommodations
    query = Accommodation.query.filter(Accommodation.isActive == True if hasattr(Accommodation, 'isActive') else True)
    
    # Availability filtering if dates are selected
    available_accommodations = []
    if start_date and end_date:
        from models import Room, AccommodationBookingLine
        start_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        all_accs = query.all()
        for acc in all_accs:
            # Check if at least one room is available
            available_rooms = False
            for room in acc.rooms:
                overlapping = AccommodationBookingLine.query.filter(
                    AccommodationBookingLine.idRoom == room.id,
                    AccommodationBookingLine.status != 'cancelled',
                    AccommodationBookingLine.startDate < end_obj,
                    AccommodationBookingLine.endDate > start_obj
                ).count()
                if overlapping == 0:
                    available_rooms = True
                    break
            if available_rooms:
                available_accommodations.append(acc)
    else:
        available_accommodations = query.limit(20).all()
    
    return render_template("tripBuilder/step-accommodation.html", 
                         accommodations=available_accommodations,
                         user=user,
                         trip_data=trip_data)


@tripBuilderBlueprint.route("/step/accommodation", methods=["POST"])
def save_accommodation():
    """Save accommodation selection"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    
    action = request.form.get("action")
    if action == "add":
        acc_id = request.form.get("accommodation_id")
        if acc_id:
            acc = Accommodation.query.get(acc_id)
            if acc and acc.rooms:
                first_room = acc.rooms[0]
                session['trip_builder']['items'].append({
                    'type': 'accommodation',
                    'id': acc.id,
                    'price': float(first_room.priceNight),
                    'details': json.dumps({'name': acc.name, 'address': acc.address})
                })
                session.modified = True
                flash(f"Alojamiento '{acc.name}' añadido al viaje.", "success")
    
    return redirect(url_for("tripBuilder.step_flights"))


# ===== STEP 2: FLIGHTS =====

@tripBuilderBlueprint.route("/step/flights", methods=["GET"])
def step_flights():
    """Step 2: Select flights"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    trip_data = session['trip_builder']
    start_date = trip_data.get('start_date')
    end_date = trip_data.get('end_date')
    
    query = Flight.query
    
    if start_date and end_date:
        start_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        # Show flights that occur within the trip window
        # Adjusting query to show flights starting after trip start and before trip end
        query = query.filter(Flight.startDate >= start_obj, Flight.startDate <= end_obj)
    
    flights = query.limit(20).all()
    
    return render_template("tripBuilder/step-flights.html",
                         flights=flights,
                         user=user,
                         trip_data=trip_data)


@tripBuilderBlueprint.route("/step/flights", methods=["POST"])
def save_flight():
    """Save flight selection"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    
    action = request.form.get("action")
    if action == "add":
        flight_id = request.form.get("flight_id")
        if flight_id:
            flight = Flight.query.get(flight_id)
            if flight:
                session['trip_builder']['items'].append({
                    'type': 'flight',
                    'id': flight.idFlight,
                    'price': float(flight.price),
                    'details': json.dumps({
                        'aeroline': flight.aeroline,
                        'origin': flight.locationStart.city if flight.locationStart else 'Origen',
                        'destination': flight.locationEnd.city if flight.locationEnd else 'Destino'
                    })
                })
                session.modified = True
                flash("Vuelo añadido al viaje.", "success")
    
    return redirect(url_for("tripBuilder.step_cruises"))


# ===== STEP 3: CRUISES =====

@tripBuilderBlueprint.route("/step/cruises", methods=["GET"])
def step_cruises():
    """Step 3: Select cruises"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    trip_data = session['trip_builder']
    start_date = trip_data.get('start_date')
    end_date = trip_data.get('end_date')
    
    from models import CruiseRoute
    query = CruiseRoute.query
    
    if start_date and end_date:
        start_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        # Show routes that overlap with trip window
        query = query.filter(CruiseRoute.startDate < end_obj, CruiseRoute.endDate > start_obj)
    
    routes = query.limit(20).all()
    
    # Prepare data for frontend (stops and segments for each route)
    routes_data = {}
    for route in routes:
        # Get stops sorted by order
        stops = sorted(route.stops, key=lambda x: x.stopOrder)
        stops_data = [{
            'id': stop.idCruiseStop,
            'name': stop.location.city,
            'order': stop.stopOrder,
            'date': stop.arrivalDate.strftime('%d/%m/%Y'),
            'idLocation': stop.idLocation
        } for stop in stops]
        
        # Get segments
        segments_data = []
        for seg in route.segments:
            segments_data.append({
                'origin': seg.idStopOrigin,
                'destination': seg.idStopDestination,
                'price': seg.price
            })
            
        routes_data[route.idCruiseRoute] = {
            'stops': stops_data,
            'segments': segments_data,
            'base_price': segments_data[0]['price'] if segments_data else 500
        }
    
    return render_template("tripBuilder/step-cruises.html",
                         routes=routes,
                         user=user,
                         trip_data=trip_data,
                         routes_data=routes_data)


@tripBuilderBlueprint.route("/step/cruises", methods=["POST"])
def save_cruise():
    """Save cruise selection"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    
    action = request.form.get("action")
    if action == "add":
        route_id = request.form.get("route_id")
        origin_id = request.form.get("origin_id")
        destination_id = request.form.get("destination_id")
        
        if route_id:
            from models import CruiseRoute, CruiseStops
            route = CruiseRoute.query.get(route_id)
            if route:
                price = 0.0
                start_date_str = ""
                end_date_str = ""
                origin_name = ""
                destination_name = ""
                
                # If specific stops are selected
                if origin_id and destination_id:
                    origin_stop = CruiseStops.query.get(origin_id)
                    dest_stop = CruiseStops.query.get(destination_id)
                    
                    if origin_stop and dest_stop and origin_stop.idCruiseRoute == route.idCruiseRoute and dest_stop.idCruiseRoute == route.idCruiseRoute:
                        # Calculate price based on segments
                        # We need to find all segments that form the path from origin to destination
                        # Assuming sequential stops for simplicity: sum price of segments between start_order and end_order
                        
                        start_order = origin_stop.stopOrder
                        end_order = dest_stop.stopOrder
                        
                        current_order = start_order
                        while current_order < end_order:
                            # Find segment starting at current_order
                            # This logical simplification assumes segments are linked. 
                            # In practice, we look for a segment where idStopOrigin has stopOrder == current_order
                            
                            segment = None
                            for seg in route.segments:
                                if seg.stop_origin.stopOrder == current_order:
                                    segment = seg
                                    break
                            
                            if segment:
                                price += segment.price
                                current_order = segment.stop_destination.stopOrder
                            else:
                                # Break if no connecting segment found (should not happen if data is consistent)
                                break
                                
                        start_date_str = origin_stop.departureDate.strftime('%d/%m/%Y')
                        end_date_str = dest_stop.arrivalDate.strftime('%d/%m/%Y')
                        origin_name = origin_stop.location.city
                        destination_name = dest_stop.location.city
                
                # Fallback to default full route if calculation failed or specific stops not selected
                if price == 0.0:
                    if route.segments:
                        price = sum(s.price for s in route.segments) # Approximate full price
                    else:
                        price = 500.0
                    start_date_str = route.startDate.strftime('%d/%m/%Y')
                    end_date_str = route.endDate.strftime('%d/%m/%Y')
                    origin_name = route.stops[0].location.city if route.stops else "Inicio"
                    destination_name = route.stops[-1].location.city if route.stops else "Fin"
                
                session['trip_builder']['items'].append({
                    'type': 'cruise',
                    'id': route.idCruiseRoute,
                    'price': float(price),
                    'details': json.dumps({
                        'name': route.ship.cruiseName if route.ship else 'Crucero',
                        'description': route.description,
                        'origin': origin_name,
                        'destination': destination_name,
                        'dates': f"{start_date_str} - {end_date_str}"
                    })
                })
                session.modified = True
                flash("Crucero añadido al viaje.", "success")
    
    return redirect(url_for("tripBuilder.step_cars"))


# ===== STEP 4: CAR RENTAL =====

@tripBuilderBlueprint.route("/step/cars", methods=["GET"])
def step_cars():
    """Step 4: Select car rental"""
    # ... (same as before but checking field names)
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    trip_data = session['trip_builder']
    start_date = trip_data.get('start_date')
    end_date = trip_data.get('end_date')
    
    from models import CarRental
    # Base query for active cars
    all_cars = Car.query.filter_by(isActive=True).all()
    available_cars = []
    
    if start_date and end_date:
        start_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        for car in all_cars:
            if car.is_available(start_obj, end_obj):
                available_cars.append(car)
    else:
        available_cars = all_cars[:20]
    
    return render_template("tripBuilder/step-cars.html",
                         cars=available_cars,
                         user=user,
                         trip_data=trip_data)


@tripBuilderBlueprint.route("/step/cars", methods=["POST"])
def save_car():
    """Save car rental selection"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    
    action = request.form.get("action")
    if action == "add":
        car_id = request.form.get("car_id")
        if car_id:
            car = Car.query.get(car_id)
            if car:
                session['trip_builder']['items'].append({
                    'type': 'car_rental',
                    'id': car.idCar,
                    'price': float(car.pricePerDay),
                    'details': json.dumps({'brand': car.brand, 'model': car.model})
                })
                session.modified = True
                flash(f"Vehículo {car.brand} {car.model} añadido al viaje.", "success")
    
    return redirect(url_for("tripBuilder.step_tours"))


# ===== STEP 5: TOURS =====

@tripBuilderBlueprint.route("/step/tours", methods=["GET"])
def step_tours():
    """Step 5: Select tours/activities"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    trip_data = session['trip_builder']
    start_date = trip_data.get('start_date')
    end_date = trip_data.get('end_date')
    
    print(f"DEBUG: step_tours - Dates: {start_date} to {end_date}")
    
    query = Tour.query
    if start_date and end_date:
        from datetime import timedelta
        start_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        # Tours that occur within the trip window
        end_obj_inclusive = end_obj + timedelta(days=1)
        
        print(f"DEBUG: Filtering Tours between {start_obj} and {end_obj_inclusive}")
        
        query = query.filter(Tour.startDate >= start_obj, Tour.startDate < end_obj_inclusive)
    
    tours = query.limit(20).all()
    print(f"DEBUG: Found {len(tours)} tours")
    
    return render_template("tripBuilder/step-tours.html",
                         tours=tours,
                         user=user,
                         trip_data=trip_data)


@tripBuilderBlueprint.route("/step/tours", methods=["POST"])
def save_tour():
    """Save tour selection"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    
    action = request.form.get("action")
    if action == "add":
        tour_id = request.form.get("tour_id")
        if tour_id:
            tour = Tour.query.get(tour_id)
            if tour:
                session['trip_builder']['items'].append({
                    'type': 'tour',
                    'id': tour.idTour,
                    'price': float(tour.price),
                    'details': json.dumps({'name': tour.title})
                })
                session.modified = True
                flash("Tour añadido al viaje.", "success")
    
    return redirect(url_for("tripBuilder.step_transport"))


# ===== STEP 6: TRANSPORT =====

@tripBuilderBlueprint.route("/step/transport", methods=["GET"])
def step_transport():
    """Step 6: Select bus/train transport"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    trip_data = session['trip_builder']
    start_date = trip_data.get('start_date')
    end_date = trip_data.get('end_date')
    
    query = BusTrain.query
    if start_date and end_date:
        start_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        # Transport within trip window
        query = query.filter(BusTrain.startDate >= start_obj, BusTrain.startDate <= end_obj)
    
    transports = query.limit(20).all()
    
    return render_template("tripBuilder/step-transport.html",
                         transports=transports,
                         user=user,
                         trip_data=trip_data)


@tripBuilderBlueprint.route("/step/transport", methods=["POST"])
def save_transport():
    """Save transport selection"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    
    action = request.form.get("action")
    if action == "add":
        transport_id = request.form.get("transport_id")
        if transport_id:
            transport = BusTrain.query.get(transport_id)
            if transport:
                session['trip_builder']['items'].append({
                    'type': 'transport',
                    'id': transport.idBusTrain,
                    'price': float(transport.price),
                    'details': json.dumps({
                        'type': transport.type,
                        'origin': transport.locationStart.city if transport.locationStart else 'Origen',
                        'destination': transport.locationEnd.city if transport.locationEnd else 'Destino'
                    })
                })
                session.modified = True
                flash("Transporte añadido al viaje.", "success")
    
    return redirect(url_for("tripBuilder.summary"))


# ===== SUMMARY & CONFIRMATION =====

@tripBuilderBlueprint.route("/summary", methods=["GET"])
def summary():
    """Show trip summary with total price"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    trip_data = session['trip_builder']
    
    # Calculate total
    total = sum(item['price'] for item in trip_data['items'])
    
    return render_template("tripBuilder/summary.html",
                         user=user,
                         trip_data=trip_data,
                         total=total)


@tripBuilderBlueprint.route("/confirm", methods=["POST"])
def confirm():
    """Confirm and create the trip"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    init_trip_session()
    trip_data = session['trip_builder']
    
    if not trip_data['items']:
        flash("No has añadido ningún servicio al viaje.", "warning")
        return redirect(url_for("tripBuilder.start"))
    
    try:
        # Calculate total
        total = sum(Decimal(str(item['price'])) for item in trip_data['items'])
        
        # Create UserTrip
        user_trip = UserTrip(
            idUser=user.idUser,
            tripName=trip_data['trip_name'],
            startDate=datetime.strptime(trip_data['start_date'], '%Y-%m-%d').date() if trip_data.get('start_date') else None,
            endDate=datetime.strptime(trip_data['end_date'], '%Y-%m-%d').date() if trip_data.get('end_date') else None,
            totalPrice=total,
            status='confirmed'
        )
        db.session.add(user_trip)
        db.session.flush()  # Get the ID
        
        # Create TripItems
        for item in trip_data['items']:
            trip_item = TripItem(
                idUserTrip=user_trip.idUserTrip,
                itemType=item['type'],
                itemId=item['id'],
                itemPrice=Decimal(str(item['price'])),
                itemDetails=item.get('details')
            )
            db.session.add(trip_item)
        
        db.session.commit()
        
        # Clear session
        clear_trip_session()
        
        flash(f"¡Viaje '{user_trip.tripName}' creado exitosamente! Total: {total}€", "success")
        return redirect(url_for("tripBuilder.my_trips"))
    
    except Exception as ex:
        db.session.rollback()
        flash(f"Error al crear el viaje: {str(ex)}", "danger")
        return redirect(url_for("tripBuilder.summary"))


# ===== MY TRIPS =====

@tripBuilderBlueprint.route("/my-trips", methods=["GET"])
def my_trips():
    """List user's trips"""
    user = get_current_user()
    if not user:
        flash("Debes iniciar sesión.", "warning")
        return redirect(url_for("userBp.login"))
    
    trips = UserTrip.query.filter_by(idUser=user.idUser).order_by(UserTrip.createdAt.desc()).all()
    
    return render_template("tripBuilder/my-trips.html",
                         trips=trips,
                         user=user)


@tripBuilderBlueprint.route("/my-trips/<int:idUserTrip>", methods=["GET"])
def trip_detail(idUserTrip):
    """View trip details"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    trip = UserTrip.query.get_or_404(idUserTrip)
    
    # Check ownership
    if trip.idUser != user.idUser:
        flash("No tienes permiso para ver este viaje.", "danger")
        return redirect(url_for("tripBuilder.my_trips"))
    
    return render_template("tripBuilder/trip-detail.html",
                         trip=trip,
                         user=user)


@tripBuilderBlueprint.route("/my-trips/<int:idUserTrip>/cancel", methods=["POST"])
def cancel_trip(idUserTrip):
    """Cancel a trip"""
    user = get_current_user()
    if not user:
        return redirect(url_for("userBp.login"))
    
    trip = UserTrip.query.get_or_404(idUserTrip)
    
    # Check ownership
    if trip.idUser != user.idUser:
        flash("No puedes cancelar viajes de otros usuarios.", "danger")
        return redirect(url_for("tripBuilder.my_trips"))
    
    if trip.status == 'cancelled':
        flash("Este viaje ya está cancelado.", "warning")
        return redirect(url_for("tripBuilder.my_trips"))
    
    try:
        trip.status = 'cancelled'
        db.session.commit()
        flash("Viaje cancelado exitosamente.", "success")
    except Exception as ex:
        db.session.rollback()
        flash(f"Error al cancelar: {str(ex)}", "danger")
    
    return redirect(url_for("tripBuilder.my_trips"))
