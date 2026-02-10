from flask import Flask, render_template
from models import db
# IMPORTANTE: Importamos el objeto userBp, no la clase UserController
from controllers.UserController import userBp 

app = Flask(__name__)

# --- CONFIGURACIÓN ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@192.168.70.80:3306/proyecto_desarrollo_web'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

# --- REGISTRO DE BLUEPRINTS ---
# Esto conecta todas las rutas que definiste en UserController (login, register, logout)
# url_prefix='/auth' hará que las rutas sean: /auth/login, /auth/register
app.register_blueprint(userBp, url_prefix='/auth') 

# --- RUTA BASE (Landing Page) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    # Aquí cargamos el HTML chulo que te hice antes
    return render_template('index.html')

# --- CREAR BASE DE DATOS ---
if __name__ == '__main__':
    with app.app_context():
        # db.drop_all() # Descomenta esto SOLO si necesitas borrar todo y empezar de cero por errores de FK
        db.create_all()
    
    app.run(debug=True)
    
    
