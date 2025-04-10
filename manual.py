import os
from dotenv import load_dotenv
import openai

# ✅ Load the .env file
load_dotenv()

# ✅ Get and check API key
api_key = os.getenv("OPENAI_API_KEY")
print("📦 DEBUG Key:", api_key[:12] + "********")

# ✅ Assign key to OpenAI
openai.api_key = api_key

# ✅ Dummy test
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful farming assistant."},
            {"role": "user", "content": "Tell me something about crop rotation."}
        ]
    )
    print("✅ Response:", response['choices'][0]['message']['content'])
except Exception as e:
    print("❌ Error:", e)

