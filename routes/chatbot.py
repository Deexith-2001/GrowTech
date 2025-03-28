from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/", methods=["POST"])
def chatbot():
    data = request.get_json()
    return jsonify({"message": "Chatbot is working!", "user_input": data})
