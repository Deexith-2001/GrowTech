import mysql.connector
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

# Create a Flask Blueprint for user authentication
users_bp = Blueprint('users', __name__)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_mysql_password",
        database="agriculture_chatbot"
    )

# Signup route
@users_bp.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"error": "⚠️ All fields are required!"}), 400

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert new user into the database
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, hashed_password))
        conn.commit()
        conn.close()

        return jsonify({"message": "✅ Signup successful! You can now log in."})

    except mysql.connector.IntegrityError:
        return jsonify({"error": "⚠️ Email already registered!"}), 400
    except Exception as e:
        print("❌ Signup Error:", e)
        return jsonify({"error": "⚠️ Internal server error"}), 500

# Login route
@users_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "⚠️ All fields are required!"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch user from database
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return jsonify({"message": f"✅ Welcome, {user['name']}!"})
        else:
            return jsonify({"error": "⚠️ Invalid email or password!"}), 401

    except Exception as e:
        print("❌ Login Error:", e)
        return jsonify({"error": "⚠️ Internal server error"}), 500

# Logout route
@users_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "✅ Logged out successfully!"})
