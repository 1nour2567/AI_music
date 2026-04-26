import os
from dotenv import load_dotenv

# Try loading .env from multiple locations
possible_locations = [
    '.',
    './claudio',
    '../claudio',
]

for location in possible_locations:
    env_path = os.path.join(location, '.env')
    if os.path.exists(env_path):
        print(f"Loading .env from: {env_path}")
        load_dotenv(env_path)
        break
else:
    print("Warning: Could not find .env file")

# Test loading API key
api_key = os.getenv('KIMI_API_KEY', 'Not found')
print(f"\nKIMI_API_KEY from environment: {'Set' if api_key and api_key != 'Not found' and api_key != 'placeholder_kimi_api_key' else 'Not set'}")
print(f"API Key value: {api_key}")

# Also test from config module
try:
    print("\n--- Testing config module ---")
    from config.config import settings
    print(f"Config API Key: {'Set' if settings.kimi_api_key and settings.kimi_api_key != 'placeholder_kimi_api_key' else 'Not set'}")
    print(f"Config value: {settings.kimi_api_key}")
except Exception as e:
    print(f"Error loading config: {e}")
