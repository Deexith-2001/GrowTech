import os
import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from openai import OpenAI
import nltk
import spacy
import logging

# Initialize NLP
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load environment variables (with override)
load_dotenv(override=True)

# DEBUG: Print key prefix for confirmation
print("📦 DEBUG Key:", os.getenv("OPENAI_API_KEY")[:12] + "********")

# Load and set OpenAI key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Logging
logging.basicConfig(level=logging.INFO)
logging.info("OpenAI key loaded successfully.")

# Flask app config
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'agribot'

mysql = MySQL(app)

# Other API keys
GEOCODING_API_KEY = os.getenv("GEOCODING_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MSP_API_KEY = os.getenv("MSP_API_KEY")
MSP_API_URL = os.getenv("MSP_API_URL")

# Load NLP tools
nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()

# ---------------- Helper Functions ----------------

def translate_text(text, source_lang, target_lang):
    if not text or source_lang == target_lang:
        return text
    try:
        url = "https://libretranslate.de/translate"
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("translatedText", text)
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return text

def fetch_msp_data():
    try:
        url = f"{MSP_API_URL}?api-key={MSP_API_KEY}&format=json"
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("records", [])
    except Exception as e:
        print(f"❌ Error fetching MSP data: {e}")
        return []

def get_location_name(lat, lon):
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={GEOCODING_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()
        return result["results"][0]["formatted_address"] if result.get("results") else "Unknown Location"
    except Exception as e:
        print(f"❌ Error fetching location: {e}")
        return "Location Error"

def get_weather_info(location):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("cod") == 200:
            weather = data["weather"][0]["description"].capitalize()
            temperature = data["main"]["temp"]
            return f"🌦 The weather in {location} is {weather} with a temperature of {temperature}°C."
        return "⚠️ Weather data not available."
    except Exception as e:
        print(f"❌ Error fetching weather: {e}")
        return "⚠️ Error fetching weather."

def analyze_sentiment(message):
    scores = sia.polarity_scores(message)
    if scores["compound"] >= 0.05:
        return "positive"
    elif scores["compound"] <= -0.05:
        return "negative"
    return "neutral"

def get_gpt_response(user_message, user_location):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an intelligent farming assistant. The user is from {user_location}."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return "⚠️ Unable to fetch a response from AI."

def get_chatbot_response(user_message, user_location):
    if any(keyword in user_message.lower() for keyword in ["weather", "temperature", "climate", "humidity"]):
        return get_weather_info(user_location)
    return get_gpt_response(user_message, user_location)

# ---------------- Routes ----------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/crops')
def crops():
    return render_template('crops.html')

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        selected_lang = data.get("language", "en")
        manual_location = data.get("location", "").strip()
        lat = data.get("latitude")
        lon = data.get("longitude")

        if manual_location:
            user_location = manual_location
        elif lat and lon:
            user_location = get_location_name(lat, lon)
        else:
            user_location = "Hyderabad"

        if not user_message:
            return jsonify({"response": "⚠️ Your message cannot be empty."}), 400

        if selected_lang != "en":
            user_message_en = translate_text(user_message, selected_lang, "en")
        else:
            user_message_en = user_message

        chatbot_response_en = get_chatbot_response(user_message_en, user_location)

        if selected_lang != "en":
            final_response = translate_text(chatbot_response_en, "en", selected_lang)
        else:
            final_response = chatbot_response_en

        return jsonify({"response": final_response})
    except Exception as e:
        print(f"❌ Error processing chat: {e}")
        return jsonify({"response": "⚠️ Internal server error."}), 500

@app.route('/api/msp')
def get_msp():
    msp_data = fetch_msp_data()
    return jsonify(msp_data)

# ---------------- Authentication ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user[3], password_input):
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, hashed_pw))
        mysql.connection.commit()
        cur.close()
        flash("Signup successful!", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

# ---------------- Other Pages ----------------

@app.route('/irrigation')
def irrigation():
    return render_template('irrigation.html')

@app.route('/soil-health')
def soil_health():
    return render_template('soil_health.html')

@app.route('/market-prices')
def market_prices():
    return render_template('market_prices.html')

@app.route('/pestcontrol')
def pestcontrol():
    return render_template('pestcontrol.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route("/api/notify", methods=["POST"])
def notify():
    data = request.get_json()
    title = data.get("title", "AgriBot Notification")
    message = data.get("message", "")
    return jsonify({"status": "success", "message": "Notification sent."})

@app.route('/status')
def status():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    app.run(debug=True)
