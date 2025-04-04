import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch API details
MSP_API_KEY = os.getenv("MSP_API_KEY")
MSP_RESOURCE_ID = os.getenv("MSP_RESOURCE_ID")
MSP_API_URL = os.getenv("MSP_API_URL")

# Check if environment variables are loaded correctly
if not MSP_API_KEY or not MSP_RESOURCE_ID or not MSP_API_URL:
    raise ValueError("❌ Missing MSP API details in .env file!")

# Construct API URL correctly
MSP_FULL_URL = f"{MSP_API_URL}/{MSP_RESOURCE_ID}?api-key={MSP_API_KEY}&format=json"

# Print the corrected URL
print("✅ Corrected MSP API URL:", MSP_FULL_URL)
