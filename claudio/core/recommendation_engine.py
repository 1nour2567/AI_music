from typing import List, Dict, Any, Optional
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models.music import Song, Playlist, PlaylistSong, UserMusicHistory
from core.scene_aware_engine import SceneAwareEngine
from config.config import settings
import chromadb
import numpy as np


class RecommendationEngine:
    """Music recommendation engine"""
    
    def __init__(self):
        """Initialize the recommendation engine"""
        self.engine = create_engine(settings.database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.scene_engine = SceneAwareEngine()
        
        # Initialize ChromaDB for vector similarity search
        self.chroma_client = chromadb.Client()
        self.song_collection = self.chroma_client.get_or_create_collection(name="songs")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user music preferences"""
        session = self.Session()
        try:
            # Get user listening history
            history = session.query(UserMusicHistory).filter_by(user_id=user_id).all()
            
            # Analyze preferences
            preferences = {
                "frequent_songs": {},
                "frequent_genres": {},
                "time_preferences": {},
                "mood_preferences": {}
            }
            
            for item in history:
                # Count song frequency
                preferences["frequent_songs"][item.song_id] = preferences["frequent_songs"].get(item.song_id, 0) + 1
                
                # Get song details
                song = session.query(Song).filter_by(id=item.song_id).first()
                if song:
                    # Count genre frequency
                    for genre in song.genre or []:
                        preferences["frequent_genres"][genre] = preferences["frequent_genres"].get(genre, 0) + 1
                
                # Analyze time preferences
                if item.context:
                    time_of_day = item.context.get("timeOfDay")
                    if time_of_day:
                        if time_of_day not in preferences["time_preferences"]:
                            preferences["time_preferences"][time_of_day] = {}
                        preferences["time_preferences"][time_of_day][item.song_id] = preferences["time_preferences"][time_of_day].get(item.song_id, 0) + 1
                    
                    # Analyze mood preferences
                    mood = item.context.get("mood")
                    if mood:
                        if mood not in preferences["mood_preferences"]:
                            preferences["mood_preferences"][mood] = {}
                        preferences["mood_preferences"][mood][item.song_id] = preferences["mood_preferences"][mood].get(item.song_id, 0) + 1
            
            return preferences
        finally:
            session.close()
    
    def calculate_song_score(self, song_id: str, user_id: str, context: Dict[str, Any]) -> float:
        """Calculate score for a song based on user preferences and context"""
        session = self.Session()
        try:
            song = session.query(Song).filter_by(id=song_id).first()
            if not song:
                return 0.0
            
            score = 0.0
            
            # Get user preferences
            preferences = self.get_user_preferences(user_id)
            
            # 1. Historical preference score (40%)
            historical_score = preferences["frequent_songs"].get(song_id, 0) * 0.4
            score += historical_score
            
            # 2. Genre preference score (20%)
            genre_score = 0.0
            for genre in song.genre or []:
                genre_score += preferences["frequent_genres"].get(genre, 0)
            genre_score = genre_score * 0.2
            score += genre_score
            
            # 3. Time context score (15%)
            time_of_day = context.get("time", {}).get("time_of_day")
            if time_of_day:
                time_score = preferences["time_preferences"].get(time_of_day, {}).get(song_id, 0) * 0.15
                score += time_score
            
            # 4. Mood context score (15%)
            user_mood = context.get("user_mood")
            if user_mood:
                mood_score = preferences["mood_preferences"].get(user_mood, {}).get(song_id, 0) * 0.15
                score += mood_score
            
            # 5. Weather context score (10%)
            weather = context.get("weather", {})
            if weather:
                weather_condition = weather.get("condition")
                # Map weather to appropriate music features
                if weather_condition == "Clear":
                    # Prefer energetic, happy songs
                    if song.features:
                        energy = song.features.get("energy", 0)
                        valence = song.features.get("valence", 0)
                        weather_score = (energy + valence) * 0.05
                        score += weather_score
                elif weather_condition == "Rain":
                    # Prefer calm, acoustic songs
                    if song.features:
                        acousticness = song.features.get("acousticness", 0)
                        energy = song.features.get("energy", 0)
                        weather_score = (acousticness + (1 - energy)) * 0.05
                        score += weather_score
            
            return score
        finally:
            session.close()
    
    def get_recommendations(self, user_id: str, context: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Get music recommendations for the user"""
        session = self.Session()
        try:
            # Get all songs
            songs = session.query(Song).all()
            
            # Calculate scores for each song
            song_scores = []
            for song in songs:
                score = self.calculate_song_score(song.id, user_id, context)
                song_scores.append((song, score))
            
            # Sort songs by score
            song_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Get top recommendations
            recommendations = []
            for song, score in song_scores[:limit]:
                recommendations.append({
                    "id": song.id,
                    "title": song.title,
                    "artist": song.artist,
                    "album": song.album,
                    "genre": song.genre,
                    "duration": song.duration,
                    "score": score
                })
            
            return recommendations
        finally:
            session.close()
    
    def get_contextual_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recommendations based on current context"""
        # Get current context
        context = self.scene_engine.get_full_context(user_id)
        
        # Get recommendations
        return self.get_recommendations(user_id, context, limit)


# Example usage
if __name__ == "__main__":
    engine = RecommendationEngine()
    recommendations = engine.get_contextual_recommendations("default", limit=5)
    print("Recommended songs:")
    for i, song in enumerate(recommendations, 1):
        print(f"{i}. {song['title']} by {', '.join(song['artist'])} (Score: {song['score']:.2f})")
