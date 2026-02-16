from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models import Cruise, CruiseStops, CruiseSegment
from models import db, Location, User

cruiseBp = Blueprint('cruise', __name__)

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)

@cruiseBp.route("/", methods=["GET"])
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

@cruiseBp.route("/my", methods=["GET"])
def my_cruises():
    user = get_current_user()
    if not user or user.role != "company":
        flash("Solo las compañías pueden ver sus cruceros.")
        return redirect(url_for("cruise.list_cruises"))
    cruises = Cruise.query.join(Cruise).filter(Cruise.idCompany == user.idUser).all()
    return render_template("my_cruises.html", cruises=cruises, user=user)

@cruiseBp.route("/create", methods=["GET", "POST"])
def create_cruise():
    user = get_current_user()
    if not user or user.role != "company":
        flash("Solo las compañías pueden crear cruceros.")
        return redirect(url_for("cruise.list_cruises"))
        
    ships = Cruise.query.filter_by(idCompany=user.idUser).all()
    locations = Location.query.all()
    
    if request.method == "POST":
        idShip = request.form["idShip"]
        startDate = datetime.strptime(request.form["startDate"], "%Y-%m-%dT%H:%M")
        endDate = datetime.strptime(request.form["endDate"], "%Y-%m-%dT%H:%M")
        description = request.form["description"]
        
        # 1. Crear el Crucero
        cruise = Cruise(idShip=idShip, startDate=startDate, endDate=endDate, description=description, idCompany=user.idUser)
        db.session.add(cruise)
        db.session.flush() 

        # --- PROCESAR PARADAS ---
        stops_data = []
        for i in range(1, 6):
            loc_id = request.form.get(f'stop_location_{i}')
            if not loc_id or loc_id == "":
                continue
                
            arrival_str = request.form.get(f'stop_arrival_{i}')
            departure_str = request.form.get(f'stop_departure_{i}')
            
            if arrival_str and departure_str:
                stops_data.append({
                    'idLocation': int(loc_id),
                    'stopOrder': int(request.form[f'stop_order_{i}']),
                    'arrivalDate': datetime.strptime(arrival_str, "%Y-%m-%dT%H:%M"),
                    'departureDate': datetime.strptime(departure_str, "%Y-%m-%dT%H:%M")
                })
        
        # Validar que hay al menos 2 paradas para definir ruta
        if len(stops_data) < 2:
            flash("Debe definir al menos 2 paradas para crear la ruta.", "warning")
            db.session.rollback()
            return render_template("cruise_form.html", ships=ships, user=user, locations=locations)

        # 2. Crear la Ruta (CruiseRoute)
        # Asumimos que la primera parada es el inicio y la última el fin
        sorted_stops = sorted(stops_data, key=lambda x: x['stopOrder'])
        from models.CruiseRoute import CruiseRoute # Importar aquí para evitar circular imports si los hubiera
        
        route = CruiseRoute(
            idCruise=cruise.idCruise,
            startDate=startDate,
            endDate=endDate,
            idStartLocation=sorted_stops[0]['idLocation'],
            idEndLocation=sorted_stops[-1]['idLocation'],
            description=description
        )
        db.session.add(route)
        db.session.flush() # Para obtener idCruiseRoute

        # 3. Crear los CruiseStops vinculados a la Ruta
        created_stops_objs = []
        for stop_info in sorted_stops:
            stop = CruiseStops(
                idCruiseStop=None, # Auto-increment
                idCruiseRoute=route.idCruiseRoute, # Usar el ID de la ruta creada
                idLocation=stop_info['idLocation'],
                stopOrder=stop_info['stopOrder'],
                arrivalDate=stop_info['arrivalDate'],
                departureDate=stop_info['departureDate']
            )
            db.session.add(stop)
            created_stops_objs.append(stop)
        
        db.session.flush()

        # 4. Crear los Segmentos (CruiseSegment)
        for j in range(1, 5): 
            origin_order_str = request.form.get(f'segment_origin_{j}')
            dest_order_str = request.form.get(f'segment_dest_{j}')
            price_str = request.form.get(f'segment_price_{j}')

            if origin_order_str and dest_order_str and price_str:
                origin_order = int(origin_order_str)
                dest_order = int(dest_order_str)
                price = float(price_str)
                
                # Buscar los IDs de los stops recien creados
                stop_origin = next((s for s in created_stops_objs if s.stopOrder == origin_order), None)
                stop_dest = next((s for s in created_stops_objs if s.stopOrder == dest_order), None)
                
                if stop_origin and stop_dest:
                    segment = CruiseSegment(
                        idCruise=cruise.idCruise, # Algunos modelos vinculan segmento a crucero
                        idRoute=route.idCruiseRoute, # Otros a la ruta
                        idStopOrigin=stop_origin.idCruiseStop,
                        idStopDestination=stop_dest.idCruiseStop,
                        price=price
                    )
                    db.session.add(segment)

        db.session.commit()
        flash("¡Crucero creado con éxito!", "success")
        return redirect(url_for("cruise.my_cruises"))
        
    return render_template("cruise_form.html", ships=ships, user=user, locations=locations)

@cruiseBp.route("/<int:idCruise>", methods=["GET"])
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
