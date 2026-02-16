from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models.Cruise import Cruise, Ship, CruiseStop, CruiseSegment
from models import db, Location, User

cruise_bp = Blueprint("cruise", __name__, url_prefix="/cruises")

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)

@cruise_bp.route("/", methods=["GET"])
def list_cruises():
    user = get_current_user()
    city_from = request.args.get('from')
    city_to = request.args.get('to')
    cruises = Cruise.query.all()
    locations = Location.query.all()
    filtered = []
    for cruise in cruises:
        stops = sorted(cruise.cruiseStops, key=lambda s: s.stopOrder)
        if city_from and city_to:
            try:
                idx_from = next(i for i, s in enumerate(stops) if str(s.idLocation) == city_from)
                idx_to = next(i for i, s in enumerate(stops) if str(s.idLocation) == city_to)
                if idx_from < idx_to:
                    # Calcular precio parcial
                    segments = sorted(cruise.cruiseSegments, key=lambda seg: seg.idCruiseSegment)
                    price = 0
                    for seg in segments:
                        so = next((s for s in stops if s.idCruiseStop == seg.idStopOrigin), None)
                        sd = next((s for s in stops if s.idCruiseStop == seg.idStopDestination), None)
                        if so and sd and idx_from <= stops.index(so) < stops.index(sd) <= idx_to:
                            price += seg.price
                    filtered.append({'cruise': cruise, 'price': price, 'from': city_from, 'to': city_to})
            except StopIteration:
                continue
        else:
            # Precio total
            total_price = sum(seg.price for seg in cruise.cruiseSegments)
            filtered.append({'cruise': cruise, 'price': total_price, 'from': None, 'to': None})
    return render_template("cruise_list.html", cruises=filtered, user=user, locations=locations)

@cruise_bp.route("/my", methods=["GET"])
def my_cruises():
    user = get_current_user()
    if not user or user.role != "company":
        flash("Solo las compañías pueden ver sus cruceros.")
        return redirect(url_for("cruise.list_cruises"))
    cruises = Cruise.query.join(Ship).filter(Ship.idCompany == user.idUser).all()
    return render_template("my_cruises.html", cruises=cruises, user=user)

@cruise_bp.route("/create", methods=["GET", "POST"])
def create_cruise():
    user = get_current_user()
    if not user or user.role != "company":
        flash("Solo las compañías pueden crear cruceros.")
        return redirect(url_for("cruise.list_cruises"))
        
    ships = Ship.query.filter_by(idCompany=user.idUser).all()
    locations = Location.query.all()
    
    if request.method == "POST":
        idShip = request.form["idShip"]
        startDate = datetime.strptime(request.form["startDate"], "%Y-%m-%dT%H:%M")
        endDate = datetime.strptime(request.form["endDate"], "%Y-%m-%dT%H:%M")
        description = request.form["description"]
        
        cruise = Cruise(idShip=idShip, startDate=startDate, endDate=endDate, description=description)
        db.session.add(cruise)
        db.session.flush() 

        # --- PROCESAR PARADAS ---
        stops = []
        for i in range(1, 6): # Usamos range(1, 6) porque en el HTML pusimos 5 campos
            loc_id = request.form.get(f'stop_location_{i}')
            
            # CAMBIO AQUÍ: Validamos que el usuario haya seleccionado una ubicación
            # Si el campo está vacío, saltamos a la siguiente iteración
            if not loc_id or loc_id == "":
                continue
                
            arrival_str = request.form.get(f'stop_arrival_{i}')
            departure_str = request.form.get(f'stop_departure_{i}')
            
            # Validamos que las fechas no estén vacías antes de convertirlas
            if arrival_str and departure_str:
                stop = CruiseStop(
                    idCruise=cruise.idCruise,
                    idRoute=1,
                    idLocation=int(loc_id),
                    stopOrder=int(request.form[f'stop_order_{i}']),
                    arrivalDate=datetime.strptime(arrival_str, "%Y-%m-%dT%H:%M"),
                    departureDate=datetime.strptime(departure_str, "%Y-%m-%dT%H:%M")
                )
                db.session.add(stop)
                stops.append(stop)
        
        db.session.flush()

        # --- PROCESAR TRAMOS ---
        for j in range(1, 5): # El HTML tiene 4 bloques de segmentos
            origin_order_str = request.form.get(f'segment_origin_{j}')
            dest_order_str = request.form.get(f'segment_dest_{j}')
            price_str = request.form.get(f'segment_price_{j}')

            # CAMBIO AQUÍ: Solo procesamos si el usuario llenó los datos del segmento
            if origin_order_str and dest_order_str and price_str:
                origin_order = int(origin_order_str)
                dest_order = int(dest_order_str)
                price = float(price_str)
                
                stop_origin = next((s for s in stops if s.stopOrder == origin_order), None)
                stop_dest = next((s for s in stops if s.stopOrder == dest_order), None)
                
                if stop_origin and stop_dest:
                    segment = CruiseSegment(
                        idCruise=cruise.idCruise,
                        idRoute=1,
                        idStopOrigin=stop_origin.idCruiseStop,
                        idStopDestination=stop_dest.idCruiseStop,
                        price=price
                    )
                    db.session.add(segment)

        db.session.commit()
        flash("¡Crucero creado con éxito!")
        return redirect(url_for("cruise.my_cruises"))
        
    return render_template("cruise_form.html", ships=ships, user=user, locations=locations)

@cruise_bp.route("/<int:idCruise>", methods=["GET"])
def cruise_detail(idCruise):
    cruise = Cruise.query.get_or_404(idCruise)
    city_from = request.args.get('from')
    city_to = request.args.get('to')
    stops = sorted(cruise.cruiseStops, key=lambda s: s.stopOrder)
    filtered_stops = stops
    filtered_segments = cruise.cruiseSegments
    if city_from and city_to:
        try:
            idx_from = next(i for i, s in enumerate(stops) if str(s.idLocation) == city_from)
            idx_to = next(i for i, s in enumerate(stops) if str(s.idLocation) == city_to)
            if idx_from < idx_to:
                filtered_stops = stops[idx_from:idx_to+1]
                filtered_segments = [seg for seg in cruise.cruiseSegments if seg.stop_origin in filtered_stops and seg.stop_destination in filtered_stops]
        except StopIteration:
            pass
    return render_template("cruise_detail.html", cruise=cruise, stops=filtered_stops, segments=filtered_segments)
