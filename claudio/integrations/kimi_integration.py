import requests
import json
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv


class KimiIntegration:
    """Integration with Kimi 2.6 API"""
    
    def __init__(self):
        """Initialize Kimi integration"""
        # Load from .env file first
        load_dotenv()
        
        # Load from environment variables directly
        self.api_key = os.getenv('KIMI_API_KEY', 'placeholder_kimi_api_key')
        self.model = os.getenv('KIMI_MODEL', 'kimi')
        self.api_base = os.getenv('KIMI_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3/')
        
        # Print configuration for debugging
        print(f"Kimi API Key: {'Set' if self.api_key and self.api_key != 'placeholder_kimi_api_key' else 'Not set (placeholder)'}")
        print(f"Kimi Model: {self.model}")
        print(f"Kimi API Base: {self.api_base}")
    
    def generate_music_recommendation(self, user_input: str, context: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
        """Generate music recommendation response"""
        # Check if API key is set
        if not self.api_key or self.api_key == "placeholder_kimi_api_key":
            return self._generate_default_response(user_input, context, recommendations)
        
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
    
    def _generate_default_response(self, user_input: str, context: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
        """Generate a smart default response without calling the API"""
        time_of_day = context.get('time', {}).get('time_of_day', 'day')
        weather = context.get('weather', {}).get('condition', 'Sunny')
        
        greeting = ""
        if time_of_day == 'morning':
            greeting = "早上好！"
        elif time_of_day == 'afternoon':
            greeting = "下午好！"
        elif time_of_day == 'evening':
            greeting = "晚上好！"
        else:
            greeting = "晚上好！"
        
        recommendation_text = ""
        if recommendations:
            recommendation_text = f"我为您准备了{len(recommendations)}首歌曲：\n"
            for i, song in enumerate(recommendations[:3], 1):
                artists = ", ".join(song.get('artist', []))
                recommendation_text += f"{i}. {song.get('title')} - {artists}\n"
        
        if not recommendation_text:
            recommendation_text = "我已经准备了一些推荐歌曲，您可以点击推荐列表中的歌曲开始播放！"
        
        return f"{greeting}我是 Claudio，您的音乐智能助手！\n\n{recommendation_text}\n\n您可以点击上一首/下一首按钮切换歌曲，或者告诉我您想听什么类型的音乐！"
    
    def understand_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Understand user intent from input"""
        # Check if API key is set
        if not self.api_key or self.api_key == "placeholder_kimi_api_key":
            # Return default intent
            return {
                "intent": "general_chat",
                "parameters": {}
            }
        
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
        # Check if API key is set
        if not self.api_key or self.api_key == "placeholder_kimi_api_key":
            return "我的音乐收藏"
        
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
        # Check if API key is set
        if not self.api_key or self.api_key == "placeholder_kimi_api_key":
            print("Error: KIMI_API_KEY is not set or is still the placeholder value")
            return "I'm sorry, I encountered an error. Please check your API key configuration."
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Use correct model name for Kimi
        # Kimi's model name should be something like "ep-20240513170305-7h466"
        # For demonstration, we'll use a common model name
        model_name = self.model if self.model != "kimi-2.6" else "kimi"
        
        data = {
            "model": model_name,
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
            print(f"Calling Kimi API with model: {model_name}")
            print(f"API Base URL: {self.api_base}")
            
            response = requests.post(
                f"{self.api_base}chat/completions",
                headers=headers,
                json=data,
                timeout=30  # Add timeout
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text[:500]}...")  # Print first 500 chars
            
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return f"I'm sorry, I encountered a network error. Please check your internet connection and API configuration."
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
