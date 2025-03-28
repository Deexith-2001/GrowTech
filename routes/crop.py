from flask import Blueprint, request, jsonify

crop_bp = Blueprint("crop", __name__)

@crop_bp.route("/", methods=["GET"])
def get_crop_info():
    return jsonify({"message": "Crop route is working!"})
