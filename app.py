from flask import Flask
from models import db
from controllers.UserController import UserController

app = Flask(__name__)

# --- CONFIGURACIÓN ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/python_base'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

# --- RUTA BASE ---
@app.route('/', methods=['GET', 'POST'])
def index():
    return "Pagina /"

# --- RUTAS DE USUARIO (Login/Registro) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    return UserController.login()

@app.route('/register', methods=['GET', 'POST'])
def register():
    return UserController.register()

@app.route('/logout')
def logout():
    return UserController.logout()



# --- CREAR BASE DE DATOS ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)