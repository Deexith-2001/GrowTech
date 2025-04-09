from dotenv import load_dotenv
import os
import openai

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
print("📦 DEBUG Key:", key[:12] + "********")

openai.api_key = key

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me something about farming."}
        ]
    )
    print("✅ Response:", response.choices[0].message.content.strip())
except Exception as e:
    print("❌ Error:", e)
