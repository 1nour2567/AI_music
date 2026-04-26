import requests
import json
from typing import Dict, Any, Optional, List
from config.config import settings


class KimiIntegration:
    """Integration with Kimi 2.6 API"""
    
    def __init__(self):
        """Initialize Kimi integration"""
        self.api_key = settings.kimi_api_key
        self.model = settings.kimi_model
        self.api_base = settings.kimi_api_base
    
    def generate_music_recommendation(self, user_input: str, context: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
        """Generate music recommendation response"""
        prompt = f"""
You are Claudio, a smart music agent that understands user preferences and provides personalized music recommendations.

Current context:
{context}

Current recommendations:
{recommendations}

User input:
{user_input}

Please respond with a friendly, natural response that:
1. Acknowledges the user's input
2. Explains why you're recommending these songs based on the context
3. Provides the recommendations in a clear, organized way
4. Asks if they'd like to hear more recommendations or have any other requests
"""
        
        response = self._call_kimi_api(prompt)
        return response
    
    def understand_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Understand user intent from input"""
        prompt = f"""
You are a music assistant that analyzes user input to understand their intent.

User input:
{user_input}

Please classify the intent into one of the following categories:
- music_recommendation: User wants music recommendations
- mood_change: User wants to change the mood of the music
- playlist_management: User wants to manage playlists
- music_info: User asks about music information
- device_control: User wants to control music devices
- general_chat: General chat about music

Also provide any relevant parameters extracted from the input, such as:
- mood: The mood the user wants
- genre: The genre the user prefers
- artist: Specific artist mentioned
- song: Specific song mentioned
- time_of_day: Time-related preferences
- activity: Activity-related preferences

Return the result as a JSON object with 'intent' and 'parameters' fields.
"""
        
        response = self._call_kimi_api(prompt)
        
        # Parse the JSON response
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Fallback if Kimi doesn't return valid JSON
            return {
                "intent": "general_chat",
                "parameters": {}
            }
    
    def generate_playlist_name(self, songs: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Generate a playlist name based on songs and context"""
        song_list = "\n".join([f"- {song['title']} by {', '.join(song['artist'])}" for song in songs[:5]])
        
        prompt = f"""
Generate a creative and descriptive playlist name based on the following songs and context:

Songs:
{song_list}

Context:
{context}

The playlist name should:
1. Be catchy and memorable
2. Reflect the mood and style of the songs
3. Consider the current context (time of day, weather, etc.)
4. Be between 2-4 words
5. Not include the word "playlist"
"""
        
        response = self._call_kimi_api(prompt)
        return response.strip()
    
    def _call_kimi_api(self, prompt: str) -> str:
        """Call Kimi API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.api_base}chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling Kimi API: {e}")
            return "I'm sorry, I encountered an error. Please try again later."


# Example usage
if __name__ == "__main__":
    kimi = KimiIntegration()
    
    # Test music recommendation generation
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
    
    recommendations = [
        {
            "id": "song_001",
            "title": "颜色",
            "artist": ["许美静"],
            "album": "都是夜归人",
            "genre": ["华语流行", "抒情"],
            "score": 0.85
        }
    ]
    
    response = kimi.generate_music_recommendation(
        "我需要一些早上听的华语歌",
        context,
        recommendations
    )
    print("Kimi response:")
    print(response)
    
    # Test intent understanding
    intent = kimi.understand_user_intent("我现在心情有点低落，想听一些温暖的音乐")
    print("\nIntent understanding:")
    print(intent)
