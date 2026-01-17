import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load env vars
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: No API Key found.")
    sys.exit(1)

genai.configure(api_key=api_key)

print("Fetching available models from Google...")
print("-" * 40)

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
except Exception as e:
    print(f"Error fetching models: {e}")