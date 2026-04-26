from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv
from core.scene_aware_engine import SceneAwareEngine
from core.recommendation_engine import RecommendationEngine
from core.device_control import DeviceControl
from integrations.kimi_integration import KimiIntegration
from data.data_importer import MusicDataImporter
from config.config import settings

# Load .env file
load_dotenv()

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
        # Get recommendations (this will also initialize database and import sample data if needed)
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
        print(f"Error in /api/recommend: {e}")
        # Return a friendly error message instead of a 500 error
        return MusicResponse(
            response="抱歉，我遇到了一些问题。请检查服务器日志以了解详细信息。",
            recommendations=[]
        )

@app.post("/api/chat", response_model=MusicResponse)
async def chat_with_claudio(request: UserInput):
    """Chat with Claudio about music"""
    try:
        # Get current context if not provided
        context = request.context or scene_engine.get_full_context(request.user_id)
        
        # Check if API key is configured
        has_api_key = kimi_integration.api_key and kimi_integration.api_key != "placeholder_kimi_api_key"
        
        if has_api_key:
            # Use full AI capabilities when API key is set
            intent = kimi_integration.understand_user_intent(request.input)
            
            if intent["intent"] in ["music_recommendation", "mood_change"]:
                recommendations = recommendation_engine.get_contextual_recommendations(
                    request.user_id, 5
                )
                response = kimi_integration.generate_music_recommendation(
                    request.input, context, recommendations
                )
                return MusicResponse(response=response, recommendations=recommendations)
            else:
                response = kimi_integration.generate_music_recommendation(
                    request.input, context, []
                )
                return MusicResponse(response=response, recommendations=[])
        else:
            # Use smart default responses when no API key
            user_message = request.input.lower()
            recommendations = recommendation_engine.get_contextual_recommendations(
                request.user_id, 5
            )
            
            # Generate contextual responses
            response = _generate_smart_chat_response(user_message, context, recommendations)
            
            return MusicResponse(
                response=response,
                recommendations=recommendations
            )
    except Exception as e:
        print(f"Error in /api/chat: {e}")
        return MusicResponse(
            response="抱歉，我遇到了一些问题。请检查服务器日志以了解详细信息。",
            recommendations=[]
        )


def _generate_smart_chat_response(user_message: str, context: Dict, recommendations: List) -> str:
    """Generate smart chat responses without API key"""
    time_of_day = context.get('time', {}).get('time_of_day', 'day')
    
    # Common user intents
    greetings = ['你好', '您好', '嗨', 'hi', 'hello', '早上好', '下午好', '晚上好']
    music_requests = ['音乐', '歌', '听', '推荐', '播放', '唱']
    mood_requests = ['开心', '难过', '快乐', '悲伤', '忧郁', '兴奋', '安静']
    thanks = ['谢谢', '感谢', '谢了']
    goodbye = ['再见', '拜拜', '走了', '离开']
    
    user_lower = user_message.lower()
    
    # Check for common intents
    if any(greet in user_lower for greet in greetings):
        time_greeting = {
            'morning': '早上好',
            'afternoon': '下午好', 
            'evening': '晚上好',
            'night': '晚上好'
        }.get(time_of_day, '你好')
        return f"{time_greeting}！我是 Claudio，您的音乐智能助手！我为您准备了一些推荐歌曲，您可以点击上一首/下一首按钮来切换。您想听什么类型的音乐呢？"
    
    elif any(request in user_lower for request in music_requests):
        return f"好的！我为您准备了{len(recommendations)}首推荐歌曲！您可以点击推荐列表中的任意歌曲开始播放，或者用控制按钮切换。有什么特别想听的风格或歌手吗？"
    
    elif any(mood in user_lower for mood in mood_requests):
        if any(word in user_lower for word in ['难过', '悲伤', '忧郁', '不开心']):
            return "我理解您的心情。听一些温暖治愈的音乐会有帮助！我为您准备了一些舒缓的音乐，希望能让您感觉好一点。"
        elif any(word in user_lower for word in ['开心', '快乐', '兴奋']):
            return "太棒了！在这么好的心情下，听一些欢快的音乐会更棒！我为您准备了一些有活力的歌曲！"
        return "我明白您的心情！让我们用合适的音乐来配合您的心情吧。"
    
    elif any(thank in user_lower for thank in thanks):
        return "不客气！能为您服务是我的荣幸！如果有其他想听的音乐，随时告诉我！"
    
    elif any(bye in user_lower for bye in goodbye):
        return "再见！希望您享受今天的音乐。下次想听音乐时，随时找我！"
    
    else:
        return f"我收到您的消息了！我已经为您准备了{len(recommendations)}首推荐歌曲，您可以点击上一首/下一首按钮来切换，或者点击推荐列表中的任意歌曲开始播放！有什么特别想听的音乐吗？"

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
