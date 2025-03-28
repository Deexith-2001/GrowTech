import os
import requests
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Retrieve API keys securely
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Debugging: Print API keys (masked for security)
print(f"🔍 Loaded OpenAI API Key: {'SET' if OPENAI_API_KEY else 'MISSING'}")
print(f"🔍 Loaded Weather API Key: {'SET' if WEATHER_API_KEY else 'MISSING'}")

# Ensure API keys are set
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: Missing OpenAI API key. Ensure it is set in the .env file.")
if not WEATHER_API_KEY:
    raise ValueError("❌ ERROR: Missing Weather API key. Ensure it is set in the .env file.")

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API Key correctly
openai.api_key = OPENAI_API_KEY

# Function to get weather data
def get_weather(location):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            print(f"❌ Error: Weather data not found for {location}. Response: {data}")
            return None  # Location not found
        
        return {
            "location": location,
            "temperature": data['main']['temp'],
            "description": data['weather'][0]['description'],
            "humidity": data['main']['humidity']
        }
    except Exception as e:
        print(f"❌ Error fetching weather data: {e}")
        return None

# Crop recommendations based on temperature
def recommend_crops(temperature):
    if temperature > 30:
        return "🌞 Best crops for hot climate: Maize, Rice, Sugarcane, Cotton, Soybean."
    elif 20 <= temperature <= 30:
        return "🌤 Best crops for moderate climate: Wheat, Barley, Potato, Tomato, Chickpea."
    return "❄️ Best crops for cold climate: Carrot, Peas, Mustard, Cabbage, Cauliflower."

# Pest control methods
pest_methods = {
    "aphids": "🪲 Use neem oil or insecticidal soap. Introduce ladybugs to your farm.",
    "caterpillars": "🐛 Apply Bacillus thuringiensis (BT) or handpick caterpillars.",
    "whiteflies": "🦟 Use yellow sticky traps and neem-based sprays.",
    "mites": "🕷 Increase humidity and use sulfur-based sprays.",
    "Aulacophora foveicollis": "🐞 Use neem-based insecticides and remove infected plants.",
}

def pest_control(pest):
    return pest_methods.get(pest.lower(), "⚠️ Sorry, no specific information found for this pest.")

# Homepage route
@app.route("/")
def home():
    return render_template("index.html")

# Function to interact with OpenAI
def ask_gpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an agriculture expert chatbot helping farmers with crop selection, pest control, and weather advice."},
                {"role": "user", "content": message}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Error with OpenAI API: {e}")
        return "⚠️ Sorry, I couldn't process your request right now. Please try again later."

# Chatbot API route
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        user_location = data.get("location", "Hyderabad")  # Default location

        if not user_message:
            return jsonify({"response": "⚠️ Your message cannot be empty."}), 400

        # Weather-related queries
        weather_keywords = ["weather", "temperature", "humidity", "climate"]
        if any(keyword in user_message.lower() for keyword in weather_keywords):
            weather = get_weather(user_location)
            if weather:
                return jsonify({
                    "response": f"🌦 The weather in {weather['location']} is {weather['description']} with a temperature of {weather['temperature']}°C and {weather['humidity']}% humidity."
                })
            return jsonify({"response": "⚠️ Sorry, I couldn't find the weather for that location."})

        # Crop recommendation queries
        if "crops" in user_message.lower() or "best crops" in user_message.lower():
            weather = get_weather(user_location)
            if weather:
                crops = recommend_crops(weather['temperature'])
                return jsonify({"response": f"🌱 In {user_location}, {crops}"})
            return jsonify({"response": "⚠️ Sorry, I couldn't fetch weather details for crop recommendations."})

        # Pest control queries
        for pest in pest_methods.keys():
            if pest in user_message.lower():
                return jsonify({"response": pest_control(pest)})

        # Otherwise, use OpenAI for general questions
        gpt_response = ask_gpt(user_message)
        return jsonify({"response": gpt_response})

    except Exception as e:
        print(f"❌ Error in chat route: {e}")
        return jsonify({"response": "⚠️ Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
