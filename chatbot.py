# chatbot.py

import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def chatbot_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]
    )
    return response["choices"][0]["message"]["content"]
