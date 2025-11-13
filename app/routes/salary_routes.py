from flask import Blueprint, request, jsonify
from app import db
from app.models.salary import Salary

salary_bp = Blueprint('salary_bp', __name__)

@salary_bp.route('/', methods=['GET'])
def get_salaries():
    """Obtiene y devuelve todos los registros de salarios."""
    try:
        salaries = Salary.query.all()
        return jsonify([s.to_dict() for s in salaries]), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al obtener salarios', 'error': str(e)}), 500

@salary_bp.route('/<int:id>', methods=['GET'])
def get_salary(id):
    """Obtiene y devuelve un registro de salario por su ID."""
    try:
        salary = Salary.query.get_or_404(id)
        return jsonify(salary.to_dict()), 200
    except Exception as e:
        return jsonify({'message': 'Salario no encontrado o error', 'error': str(e)}), 404

@salary_bp.route('/', methods=['POST'])
def create_salary():
    """Crea un nuevo registro de salario con los datos proporcionados."""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['year', 'salary_in_usd', 'employment_type', 'job_title']):
        return jsonify({'message': 'Faltan campos requeridos'}), 400

    try:
        new_salary = Salary(
            year=data['year'],
            salary_in_usd=data['salary_in_usd'],
            employment_type=data['employment_type'],
            job_title=data['job_title'],
            location=data.get('location'), 
            experience_level=data.get('experience_level'),
            created_date=db.func.current_timestamp(),
            updated_date=db.func.current_timestamp()
        )
        
        db.session.add(new_salary)
        db.session.commit()
        return jsonify(new_salary.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al crear salario', 'error': str(e)}), 500

@salary_bp.route('/<int:id>', methods=['PUT'])
def update_salary(id):
    """Actualiza un registro de salario existente por su ID."""
    salary = Salary.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'year' in data:
            salary.year = data['year']
        if 'salary_in_usd' in data:
            salary.salary_in_usd = data['salary_in_usd']
        if 'employment_type' in data:
            salary.employment_type = data['employment_type']
        if 'job_title' in data:
            salary.job_title = data['job_title']
        if 'location' in data:
            salary.location = data['location']
        if 'experience_level' in data:
            salary.experience_level = data['experience_level']
        salary.updated_date = db.func.current_timestamp()

        db.session.commit()
        return jsonify(salary.to_dict()), 200 
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar salario', 'error': str(e)}), 500

@salary_bp.route('/<int:id>', methods=['DELETE'])
def delete_salary(id):
    """Elimina un registro de salario por su ID."""
    salary = Salary.query.get_or_404(id)
    
    try:
        db.session.delete(salary)
        db.session.commit()
        return jsonify({'message': 'Salario eliminado exitosamente'}), 204 
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al eliminar salario', 'error': str(e)}), 500