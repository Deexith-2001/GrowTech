from flask import Blueprint, request, jsonify

location_bp = Blueprint("location", __name__)

@location_bp.route("/", methods=["GET"])
def get_location():
    return jsonify({"message": "Location route is working!"})
