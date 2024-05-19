from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

app = Flask(__name__)
# Configuración de la base de datos
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_HOST = '172.19.0.3'
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

# Ruta para crear un nuevo usuario
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# Ruta para obtener un usuario por ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({'name': user.name, 'email': user.email}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

# Ruta para actualizar un usuario por ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if user:
        user.name = data['name']
        user.email = data['email']
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

# Ruta para eliminar un usuario por ID
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=4000)

