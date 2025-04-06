import os
import openai

# Load key from env
api_key = os.getenv("OPENAI_API_KEY")
print("🔐 Loaded Key:", api_key[:12] + "********")

openai.api_key = api_key

# Try simple model list API (doesn't require prompt)
try:
    models = openai.Model.list()
    print("✅ Success! Model count:", len(models.data))
except Exception as e:
    print("❌ Error:", e)
