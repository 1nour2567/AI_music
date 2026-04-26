import os
import sys
from dotenv import load_dotenv

# Add the claudio directory to the path
sys.path.append('/workspace/claudio')

from integrations.kimi_integration import KimiIntegration

# Load environment variables
load_dotenv('/workspace/claudio/.env')

# Test Kimi API
print("Testing Kimi API connection...")

try:
    kimi = KimiIntegration()
    print("Kimi integration initialized successfully")
    
    # Test generate_music_recommendation
    print("\nTesting generate_music_recommendation...")
    context = {
        "time": {
            "time_of_day": "morning",
            "day_of_week": "Monday"
        },
        "weather": {
            "condition": "Sunny",
            "temperature": 22
        }
    }
    recommendations = []
    response = kimi.generate_music_recommendation("你好", context, recommendations)
    print("Response:")
    print(response)
    
    # Test understand_user_intent
    print("\nTesting understand_user_intent...")
    intent = kimi.understand_user_intent("我想听一些轻松的音乐")
    print("Intent:")
    print(intent)
    
    # Test generate_playlist_name
    print("\nTesting generate_playlist_name...")
    songs = [{
        "id": "song_001",
        "title": "颜色",
        "artist": ["许美静"],
        "album": "都是夜归人",
        "genre": ["华语流行", "抒情"]
    }]
    playlist_name = kimi.generate_playlist_name(songs, context)
    print("Playlist name:")
    print(playlist_name)
    
except Exception as e:
    print(f"Error: {e}")
