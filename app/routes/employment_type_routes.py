from flask import Blueprint, jsonify
from app import db
from app.models.employmentType import EmploymentType

employment_type_bp = Blueprint('employment_type_bp', __name__)

@employment_type_bp.route('/', methods=['GET'])
def get_employment_types():
    employment_type = EmploymentType.query.all()
    return jsonify([u.to_dict() for u in employment_type])

@employment_type_bp.route('/<int:id>', methods=['GET'])
def get_employment_type(id):
    employment_type = EmploymentType.query.get_or_404(id)
    return jsonify(employment_type.to_dict())
