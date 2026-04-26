import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipBack, SkipForward, Send } from 'lucide-react';

function App() {
  // State for player
  const [currentSong, setCurrentSong] = useState({
    title: "颜色",
    artist: ["许美静"],
    album: "都是夜归人",
    duration: 258,
    currentTime: 78
  });
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentPlaylist, setCurrentPlaylist] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  // State for chat
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "你好！我是 Claudio，你的音乐智能助手。今天想听听什么音乐？",
      sender: "claudio",
      time: new Date().toLocaleTimeString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef(null);
  
  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Get initial recommendations
  useEffect(() => {
    fetchRecommendations();
  }, []);
  
  // Simulate progress bar update
  useEffect(() => {
    let interval;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentSong(prev => {
          if (prev.currentTime >= prev.duration) {
            setIsPlaying(false);
            return { ...prev, currentTime: 0 };
          }
          return { ...prev, currentTime: prev.currentTime + 1 };
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);
  
  // Fetch recommendations from API
  const fetchRecommendations = async () => {
    try {
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
      const data = await response.json();
      
      // Add Claude's response to messages
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        content: data.response,
        sender: "claudio",
        time: new Date().toLocaleTimeString()
      }]);
      
      setRecommendations(data.recommendations);
      setCurrentPlaylist(data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };
  
  // Handle chat input
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      id: messages.length + 1,
      content: inputMessage,
      sender: "user",
      time: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      // Send message to API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          input: inputMessage
        })
      });
      
      const data = await response.json();
      
      // Add Claude's response
      const claudeMessage = {
        id: messages.length + 2,
        content: data.response,
        sender: "claudio",
        time: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, claudeMessage]);
      
      // Update recommendations if any
      if (data.recommendations && data.recommendations.length > 0) {
        setRecommendations(data.recommendations);
        setCurrentPlaylist(data.recommendations);
        setCurrentIndex(0);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages(prev => [...prev, {
        id: messages.length + 2,
        content: "抱歉，我遇到了一些问题，请稍后再试。",
        sender: "claudio",
        time: new Date().toLocaleTimeString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle recommendation selection
  const handleSelectRecommendation = (song) => {
    const index = currentPlaylist.findIndex(s => s.id === song.id);
    if (index !== -1) {
      setCurrentIndex(index);
    }
    setCurrentSong({
      title: song.title,
      artist: song.artist,
      album: song.album,
      duration: song.duration,
      currentTime: 0
    });
    setIsPlaying(true);
  };
  
  // Handle previous song
  const handlePreviousSong = () => {
    if (currentPlaylist.length === 0) return;
    const newIndex = (currentIndex - 1 + currentPlaylist.length) % currentPlaylist.length;
    setCurrentIndex(newIndex);
    const song = currentPlaylist[newIndex];
    setCurrentSong({
      title: song.title,
      artist: song.artist,
      album: song.album,
      duration: song.duration,
      currentTime: 0
    });
    setIsPlaying(true);
  };
  
  // Handle next song
  const handleNextSong = () => {
    if (currentPlaylist.length === 0) return;
    const newIndex = (currentIndex + 1) % currentPlaylist.length;
    setCurrentIndex(newIndex);
    const song = currentPlaylist[newIndex];
    setCurrentSong({
      title: song.title,
      artist: song.artist,
      album: song.album,
      duration: song.duration,
      currentTime: 0
    });
    setIsPlaying(true);
  };
  
  // Format time (seconds to MM:SS)
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  // Calculate progress percentage
  const progressPercentage = (currentSong.currentTime / currentSong.duration) * 100;

  return (
    <div className="app">
      <header className="header">
        <h1>Claudio</h1>
        <p>智能音乐代理</p>
      </header>
      
      <main className="main-content">
        {/* Player Section */}
        <section className="player-section">
          <h2>音乐播放器</h2>
          
          <div className="current-song">
            <div className="album-art">🎵</div>
            <h3>{currentSong.title}</h3>
            <p>{currentSong.artist.join(', ')}</p>
          </div>
          
          <div className="player-controls">
            <button className="control-btn" onClick={handlePreviousSong}>
              <SkipBack size={24} />
            </button>
            <button 
              className="control-btn play"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? <Pause size={32} /> : <Play size={32} />}
            </button>
            <button className="control-btn" onClick={handleNextSong}>
              <SkipForward size={24} />
            </button>
          </div>
          
          <div className="progress-bar">
            <div 
              className="progress" 
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
          
          <div className="time-info">
            <span>{formatTime(currentSong.currentTime)}</span>
            <span>{formatTime(currentSong.duration)}</span>
          </div>
        </section>
        
        {/* Chat Section */}
        <section className="chat-section">
          <h2>与 Claudio 聊天</h2>
          
          <div className="chat-messages">
            {messages.map(message => (
              <div 
                key={message.id} 
                className={`message ${message.sender === 'user' ? 'user-message' : 'claudio-message'}`}
              >
                <div className="message-content">{message.content}</div>
                <div className="message-time">{message.time}</div>
              </div>
            ))}
            {isLoading && (
              <div className="message claudio-message">
                <div className="message-content">Claudio 正在思考...</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <div className="chat-input">
            <input 
              type="text" 
              placeholder="输入消息..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <button onClick={handleSendMessage} disabled={isLoading}>
              <Send size={20} />
            </button>
          </div>
          
          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div className="recommendations">
              <h3>推荐歌曲</h3>
              <ul className="recommendation-list">
                {recommendations.map((song, index) => (
                  <li 
                    key={song.id} 
                    className="recommendation-item"
                    onClick={() => handleSelectRecommendation(song)}
                  >
                    <h4>{song.title}</h4>
                    <p>{song.artist.join(', ')}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
