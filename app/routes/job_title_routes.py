from flask import Blueprint, request, jsonify
from app import db
from app.models.jobTitle import JobTitle

job_title_bp = Blueprint('job_title_bp', __name__)


@job_title_bp.route('/', methods=['GET'])
def get_job_titles():
    """Obtiene y devuelve todos los títulos de trabajo."""
    try:
        job_titles = JobTitle.query.all()
        return jsonify([jt.to_dict() for jt in job_titles]), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener títulos de trabajo', 'error': str(e)}), 500

@job_title_bp.route('/<int:id>', methods=['GET'])
def get_job_title(id):
    """Obtiene y devuelve un título de trabajo por su ID."""
    try:
        job_title = JobTitle.query.get_or_404(id)
        return jsonify(job_title.to_dict()), 200
    except Exception as e:
        return jsonify({'message': 'Título de trabajo no encontrado o error', 'error': str(e)}), 404


@job_title_bp.route('/', methods=['POST'])
def create_job_title():
    """Crea un nuevo título de trabajo."""
    data = request.get_json()
    if 'job_title' not in data or not data['job_title']:
        return jsonify({'message': 'El campo job_title es requerido'}), 400

    try:
        new_job_title = JobTitle(
            job_title=data['job_title']
        )
        
        db.session.add(new_job_title)
        db.session.commit()
        return jsonify(new_job_title.to_dict()), 201 
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al crear el título de trabajo', 'error': str(e)}), 500

@job_title_bp.route('/<int:id>', methods=['PUT'])
def update_job_title(id):
    """Actualiza un título de trabajo por su ID."""
    job_title = JobTitle.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'job_title' in data and data['job_title']:
            job_title.job_title = data['job_title']
        else:
            return jsonify({'message': 'Se requiere el campo job_title para la actualización'}), 400

        db.session.commit()
        return jsonify(job_title.to_dict()), 200 # 200 OK
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar el título de trabajo', 'error': str(e)}), 500

@job_title_bp.route('/<int:id>', methods=['DELETE'])
def delete_job_title(id):
    """Elimina un título de trabajo por su ID."""
    job_title = JobTitle.query.get_or_404(id)
    
    try:
        db.session.delete(job_title)
        db.session.commit()
        return jsonify({'message': 'Título de trabajo eliminado exitosamente'}), 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al eliminar el título de trabajo', 'error': str(e)}), 500