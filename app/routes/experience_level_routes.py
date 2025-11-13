from flask import Blueprint, jsonify
from app import db
from app.models.experienceLevel import ExperienceLevel

experience_level_bp = Blueprint('experience_level_bp', __name__)

@experience_level_bp.route('/', methods=['GET'])
def get_experience_levels():
    experience_level = ExperienceLevel.query.all()
    return jsonify([u.to_dict() for u in experience_level])

@experience_level_bp.route('/<int:id>', methods=['GET'])
def get_experience_level(id):
    experience_level = ExperienceLevel.query.get_or_404(id)
    return jsonify(experience_level.to_dict())
