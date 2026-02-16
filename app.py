from flask import Flask, render_template
from models import db

# --- IMPORTACIÓN DE BLUEPRINTS ---
from controllers.UserController import userBp
from controllers.CruiseController import cruiseBp
from controllers.FlightController import flight_bp
from controllers.ShipController import ship_bp
from controllers.ToursController import tour_bp
from controllers.TransportController import transport_bp
from controllers.TripController import trip_bp
from controllers.acomodationController import acomodation_bp
from controllers.carRentingController import carRentingBlueprint
from controllers.Booking import booking_bp

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Asegúrate de que la base de datos 'proyecto_desarrollo_web' exista en tu MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/proyecto_desarrollo_web'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key_provisional'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Inicialización de la base de datos con la App
db.init_app(app)

# --- REGISTRO DE BLUEPRINTS ---
# Nota: El orden importa si hay rutas solapadas. 
app.register_blueprint(userBp, url_prefix='/auth')
app.register_blueprint(cruiseBp, url_prefix='/cruises')
app.register_blueprint(flight_bp, url_prefix='/flights')
app.register_blueprint(ship_bp, url_prefix='/ships')
app.register_blueprint(tour_bp, url_prefix='/tours')
app.register_blueprint(transport_bp, url_prefix='/transports')
app.register_blueprint(trip_bp, url_prefix='/trips')
app.register_blueprint(carRentingBlueprint, url_prefix='/car-renting')
app.register_blueprint(booking_bp, url_prefix='/bookings')

# Registramos el de acomodation al final si va a manejar la raíz '/'
app.register_blueprint(acomodation_bp, url_prefix='/')

# --- MANEJO DE ERRORES COMUNES ---
@app.errorhandler(404)
def page_not_found(e):
    return "Ruta no encontrada. Revisa el registro de Blueprints.", 404

# --- INICIO DE LA APLICACIÓN ---
if __name__ == '__main__':
    with app.app_context():
        # db.drop_all() # Úsalo solo si quieres resetear las tablas por completo
        db.create_all()
        print("Base de datos verificada/creada con éxito.")
    
    # El modo debug=True permite ver cambios sin reiniciar el servidor manualmente
    app.run(debug=True)