from flask import Blueprint, jsonify
from app import db
from app.models.location import Location

location_bp = Blueprint('location_bp', __name__)

@location_bp.route('/', methods=['GET'])
def get_locations():
    location = Location.query.all()
    return jsonify([u.to_dict() for u in location])

@location_bp.route('/<int:id>', methods=['GET'])
def get_location(id):
    location = Location.query.get_or_404(id)
    return jsonify(location.to_dict())
