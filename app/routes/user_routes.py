from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['GET'])
def get_users():
    """Devuelve la lista de todos los usuarios serializados."""
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

@user_bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    """Devuelve un usuario específico por ID."""
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict()), 200

@user_bp.route('/', methods=['POST'])
def create_user():
    """Crea un nuevo usuario, hasheando la contraseña."""
    data = request.get_json()
    
    required_fields = ['email', 'password', 'name', 'role']
    if not all(k in data for k in required_fields):
        return jsonify({'message': 'Faltan campos requeridos (email, password, name, role)'}), 400

    if User.exists_by_email(data['email']):
        return jsonify({'message': 'El email ya está registrado'}), 409 

    try:
        new_user = User(
            name=data['name'],
            email=data['email'],
            role_id=data['role']
        )
        
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al crear usuario', 'error': str(e)}), 500

@user_bp.route('/<int:id>', methods=['PUT'])
def update_user(id):
    """Actualiza los datos de un usuario, incluyendo la contraseña si se proporciona."""
    user = User.query.get_or_404(id)
    data = request.get_json()

    try:
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role_id = data['role']
            
        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar usuario', 'error': str(e)}), 500

@user_bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    """Elimina un usuario por su ID."""
    user = User.query.get_or_404(id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuario eliminado exitosamente'}), 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al eliminar usuario', 'error': str(e)}), 500

@user_bp.route('/check_email', methods=['POST'])
def check_email_exists():
    """Verifica si un correo electrónico ya está registrado."""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Se requiere el campo email'}), 400

    exists = User.exists_by_email(email)
    
    return jsonify({'email': email, 'exists': exists}), 200