from flask import Blueprint, jsonify
from app import db
from app.models.role import Role

role_bp = Blueprint('role_bp', __name__)

@role_bp.route('/', methods=['GET'])
def get_roles():
    role = Role.query.all()
    return jsonify([u.to_dict() for u in role])

@role_bp.route('/<int:id>', methods=['GET'])
def get_role(id):
    role = Role.query.get_or_404(id)
    return jsonify(role.to_dict())
