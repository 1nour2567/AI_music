from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from core.scene_aware_engine import SceneAwareEngine
from core.recommendation_engine import RecommendationEngine
from core.device_control import DeviceControl
from integrations.kimi_integration import KimiIntegration
from data.data_importer import MusicDataImporter

app = FastAPI(
    title="Claudio Music Agent API",
    description="AI music agent that provides personalized music recommendations",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
scene_engine = SceneAwareEngine()
recommendation_engine = RecommendationEngine()
kimi_integration = KimiIntegration()
device_control = DeviceControl()

# Data models
class UserInput(BaseModel):
    user_id: str = "default"
    input: str
    context: Dict[str, Any] = None

class RecommendationRequest(BaseModel):
    user_id: str = "default"
    limit: int = 10
    context: Dict[str, Any] = None

class PlaylistRequest(BaseModel):
    user_id: str = "default"
    songs: List[Dict[str, Any]]
    context: Dict[str, Any] = None

class MusicResponse(BaseModel):
    response: str
    recommendations: List[Dict[str, Any]] = []

# API endpoints
@app.post("/api/recommend", response_model=MusicResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get music recommendations"""
    try:
        if request.context:
            recommendations = recommendation_engine.get_recommendations(
                request.user_id, request.context, request.limit
            )
        else:
            recommendations = recommendation_engine.get_contextual_recommendations(
                request.user_id, request.limit
            )
        
        # Get current context if not provided
        context = request.context or scene_engine.get_full_context(request.user_id)
        
        # Generate natural language response
        response = kimi_integration.generate_music_recommendation(
            "Recommend me some music",
            context,
            recommendations
        )
        
        return MusicResponse(
            response=response,
            recommendations=recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=MusicResponse)
async def chat_with_claudio(request: UserInput):
    """Chat with Claudio about music"""
    try:
        # Understand user intent
        intent = kimi_integration.understand_user_intent(request.input)
        
        # Get current context if not provided
        context = request.context or scene_engine.get_full_context(request.user_id)
        
        # Handle different intents
        if intent["intent"] in ["music_recommendation", "mood_change"]:
            # Get recommendations based on intent
            recommendations = recommendation_engine.get_contextual_recommendations(
                request.user_id, 5
            )
            
            # Generate response
            response = kimi_integration.generate_music_recommendation(
                request.input,
                context,
                recommendations
            )
            
            return MusicResponse(
                response=response,
                recommendations=recommendations
            )
        else:
            # For other intents, just generate a response
            response = kimi_integration.generate_music_recommendation(
                request.input,
                context,
                []
            )
            
            return MusicResponse(
                response=response,
                recommendations=[]
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-playlist-name")
async def generate_playlist_name(request: PlaylistRequest):
    """Generate a playlist name"""
    try:
        # Get current context if not provided
        context = request.context or scene_engine.get_full_context(request.user_id)
        
        # Generate playlist name
        playlist_name = kimi_integration.generate_playlist_name(
            request.songs,
            context
        )
        
        return {"playlist_name": playlist_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/context")
async def get_current_context(user_id: str = "default"):
    """Get current scene context"""
    try:
        context = scene_engine.get_full_context(user_id)
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/import-data")
async def import_music_data():
    """Import music data"""
    try:
        importer = MusicDataImporter()
        importer.import_data(settings.music_data_path)
        return {"message": "Data import completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Device control endpoints
@app.get("/api/devices")
async def get_devices():
    """Get list of available devices"""
    try:
        devices = device_control.discover_devices()
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/connect")
async def connect_device(device_id: str):
    """Connect to a device"""
    try:
        success = device_control.connect_device(device_id)
        if success:
            return {"message": "Device connected successfully"}
        else:
            raise HTTPException(status_code=404, detail="Device not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/disconnect")
async def disconnect_device():
    """Disconnect from current device"""
    try:
        success = device_control.disconnect_device()
        if success:
            return {"message": "Device disconnected successfully"}
        else:
            return {"message": "No device connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/play")
async def play_music(song_uri: str):
    """Play music on connected device"""
    try:
        success = device_control.play(song_uri)
        if success:
            return {"message": "Music playing"}
        else:
            raise HTTPException(status_code=400, detail="Failed to play music")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/pause")
async def pause_music():
    """Pause music on connected device"""
    try:
        success = device_control.pause()
        if success:
            return {"message": "Music paused"}
        else:
            raise HTTPException(status_code=400, detail="Failed to pause music")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/stop")
async def stop_music():
    """Stop music on connected device"""
    try:
        success = device_control.stop()
        if success:
            return {"message": "Music stopped"}
        else:
            raise HTTPException(status_code=400, detail="Failed to stop music")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/volume")
async def set_volume(volume: int):
    """Set volume on connected device"""
    try:
        success = device_control.set_volume(volume)
        if success:
            return {"message": f"Volume set to {volume}"}
        else:
            raise HTTPException(status_code=400, detail="Failed to set volume")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/devices/status")
async def get_device_status():
    """Get device status"""
    try:
        status = device_control.get_device_status()
        if status:
            return status
        else:
            return {"message": "No device connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Claudio Music Agent API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
