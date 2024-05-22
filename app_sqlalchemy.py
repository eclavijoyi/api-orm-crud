from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

app = Flask(__name__)
# Configuración de la base de datos
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_HOST = '172.19.0.5'
DB_NAME = 'orm'
DB_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Verificar si la base de datos existe, si no, crearla
engine = create_engine(DB_URI)
if not database_exists(engine.url):
    create_database(engine.url)

db = SQLAlchemy(app)

# Definición del modelo User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Creación de las tablas en la base de datos
with app.app_context():
    db.create_all()

# Ruta para la página de inicio
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# Ruta para mostrar el formulario de creación de usuario
@app.route('/user_form', methods=['GET'])
def show_user_form():
    return render_template('user_form.html')

# Ruta para crear un nuevo usuario
@app.route('/users', methods=['POST'])
def add_user():
    data = request.form
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))

# Ruta para obtener un usuario por ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({'name': user.name, 'email': user.email}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

# Ruta para mostrar el formulario de edición de usuario
@app.route('/users/edit/<int:id>', methods=['GET'])
def edit_user(id):
    user = User.query.get(id)
    if user:
        return render_template('edit_user.html', user=user)
    else:
        return redirect(url_for('index'))

# Ruta para actualizar un usuario por ID
@app.route('/users/<int:id>', methods=['POST'])
def update_user(id):
    user = User.query.get(id)
    if user:
        data = request.form
        if 'name' in data and 'email' in data:
            user.name = data['name']
            user.email = data['email']
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return jsonify({'message': 'Invalid data'}), 400
    else:
        return jsonify({'message': 'User not found'}), 404

# Ruta para mostrar la página de confirmación de eliminación
@app.route('/users/delete/<int:id>', methods=['GET'])
def confirm_delete_user(id):
    user = User.query.get(id)
    if user:
        return render_template('delete_user.html', user=user)
    else:
        return redirect(url_for('index'))

# Ruta para eliminar un usuario por ID
@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=4000)
