# 音乐 AI 代理 "z" 项目架构设计

## 项目概述

**Claudio (音乐 AI 代理 "z")** 是一个智能音乐代理，通过结合 14 年的音乐数据（3000+ 歌单）、实时天气、日程和心情信息，为用户提供 24 小时个性化电台服务。

### 核心愿景

作者希望通过 AI 放大对美好事物的感受，将传统音乐数据和设备连接转化为更丰富的体验。Claudio 作为"音乐品味本体"，不仅是播放器，更是能理解用户喜好、主动规划音乐体验的智能助手。

---

## 核心功能

### 1. 个性化推荐
- 基于用户 14 年的历史歌单数据
- 结合实时信息（天气、日程、心情）
- 时间感知：早晨播放华语歌（如许美静《颜色》），工作时切换轻音乐等

### 2. 多维度联动
- **前端**: 播放器 + 聊天界面
- **后端**: 连接音响设备、音乐 API、Claude Code
- 无缝切换：听音乐 + 聊音乐

### 3. 动态调整
- 用户可通过聊天界面与 Claudio 交互
- 实时调整歌单或获取音乐推荐

---

## 系统架构

### 整体架构图

```
┌──────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│  ┌──────────────────┐          ┌──────────────────┐         │
│  │   音乐播放器     │          │    聊天界面      │         │
│  │  (播放控制)      │          │  (自然语言交互)   │         │
│  └────────┬─────────┘          └─────────┬────────┘         │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            └──────────────┬───────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                    后端服务层                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                 Claude Code Agent                      │ │
│  │  (音乐理解、推荐逻辑、对话处理)                         │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────┴───────────────────────────────┐ │
│  │                    核心服务模块                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │  音乐推荐    │  │  场景感知    │  │  对话管理    │ │ │
│  │  │   引擎      │  │    引擎      │  │    模块      │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │  设备控制    │  │  数据管理    │  │  集成接口    │ │ │
│  │  │    模块      │  │    模块      │  │    层        │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┼───────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────┴───────┐  ┌────────┴────────┐  ┌─────┴──────────┐
│  音乐数据层   │  │  实时信息层      │  │  设备控制层    │
│  (3000+歌单)  │  │ (天气/日程/心情)│  │ (音响设备)     │
└───────────────┘  └─────────────────┘  └────────────────┘
```

---

## 核心模块设计

### 1. 前端层

#### 1.1 音乐播放器模块
**职责**: 音乐播放控制，可视化展示

**功能**:
- 播放/暂停/上一首/下一首
- 音量控制
- 播放进度显示
- 播放历史
- 可视化效果（可选）

**技术选型建议**:
- Web: React/Vue + Web Audio API
- 桌面: Electron
- 移动端: React Native/Flutter

#### 1.2 聊天界面模块
**职责**: 自然语言交互，用户与 Claudio 对话

**功能**:
- 消息输入和显示
- 对话历史
- 快捷指令（如"换首歌"、"现在天气如何"）
- 支持 Markdown/富文本展示音乐信息

---

### 2. 后端服务层

#### 2.1 Claude Code Agent (核心智能体)
**职责**: 音乐理解、推荐逻辑、对话处理的核心

**功能**:
- 理解用户音乐偏好（历史数据）
- 分析实时场景信息
- 生成音乐推荐
- 处理用户对话请求
- 动态调整播放列表

**技术实现**:
- 基于 Trae Agent 框架（我们刚分析的项目）
- 集成 Claude Code API
- 自定义工具集：音乐搜索、歌单管理等

#### 2.2 音乐推荐引擎
**职责**: 根据用户偏好和场景生成个性化推荐

**核心算法**:
```
推荐评分 = 历史偏好权重(0.4) + 场景匹配(0.3) + 实时情绪(0.2) + 时间因素(0.1)
```

**数据输入**:
- 14 年歌单数据（结构化）
- 用户实时输入
- 外部实时信息

#### 2.3 场景感知引擎
**职责**: 收集和分析实时场景信息

**信息源**:
- **天气**: 天气 API（如 OpenWeatherMap）
- **日程**: 日历 API（Google Calendar, 苹果日历等）
- **心情**: 用户输入或通过音乐选择推断
- **时间**: 当前时间、星期几等
- **位置**: 可选，基于位置的场景

#### 2.4 对话管理模块
**职责**: 管理与用户的对话流程

**功能**:
- 上下文维护
- 意图识别（音乐推荐、调整、查询等）
- 对话状态管理
- 自然语言生成（回应）

#### 2.5 设备控制模块
**职责**: 连接和控制音响设备

**支持的设备**:
- Sonos
- HomePod
- Chromecast
- 蓝牙音箱
- 其他智能音响

**协议**:
- UPnP/DLNA
- AirPlay
- 厂商特定 API

#### 2.6 数据管理模块
**职责**: 管理所有数据

**数据类型**:
- 用户音乐历史
- 歌单数据
- 交互历史
- 场景日志
- 用户配置

**存储**:
- 结构化数据：SQLite/PostgreSQL
- 向量存储：Pinecone/Chroma（用于音乐相似度）
- 文件存储：本地或云存储

#### 2.7 集成接口层
**职责**: 与外部服务集成

**集成对象**:
- 音乐 API（Spotify, Apple Music, 网易云音乐等）
- 天气 API
- 日历 API
- 设备 API
- Claude Code API

---

### 3. 数据层

#### 3.1 音乐数据结构
**14 年音乐数据，3000+ 歌单的结构化设计**:

```typescript
interface Song {
  id: string;
  title: string;
  artist: string[];
  album: string;
  genre: string[];
  releaseYear: number;
  duration: number;
  // 音乐特征
  features: {
    tempo: number;
    energy: number;
    valence: number; // 情绪积极度
    danceability: number;
    acousticness: number;
    // ... 更多特征
  };
}

interface Playlist {
  id: string;
  name: string;
  description: string;
  createdAt: Date;
  updatedAt: Date;
  songs: Song[];
  // 元数据：创建时的场景
  context?: {
    timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
    season?: 'spring' | 'summer' | 'autumn' | 'winter';
    weather?: string;
    mood?: string;
    activity?: string;
  };
}

interface UserMusicHistory {
  userId: string;
  playlists: Playlist[];
  listeningHistory: {
    songId: string;
    timestamp: Date;
    context?: Playlist['context'];
    skipRate: number; // 跳过率，可能代表不喜欢
  }[];
}
```

#### 3.2 实时数据结构
```typescript
interface RealTimeContext {
  timestamp: Date;
  timeOfDay: string;
  dayOfWeek: number;
  weather: {
    condition: string;
    temperature: number;
    humidity: number;
  };
  calendar: {
    events: CalendarEvent[];
    currentEvent?: CalendarEvent;
    nextEvent?: CalendarEvent;
  };
  userMood?: string; // 用户当前心情
  location?: {
    lat: number;
    lng: number;
    placeType?: string;
  };
}
```

---

## 工作流程

### 主流程：24 小时个性化电台

```
1. 系统初始化
   ├─ 加载用户音乐历史
   ├─ 初始化场景感知引擎
   └─ 连接音乐 API 和设备

2. 实时信息采集（持续）
   ├─ 获取天气更新
   ├─ 读取日历日程
   ├─ 时间更新
   └─ 用户输入监控

3. 生成/更新播放列表
   ├─ Claude Code 分析：历史 + 场景
   ├─ 推荐引擎计算评分
   ├─ 生成当前播放列表
   └─ 推送到播放器

4. 播放和监控
   ├─ 播放器播放音乐
   ├─ 监控用户行为（跳过、收藏等）
   └─ 更新用户偏好模型

5. 用户交互
   ├─ 用户通过聊天界面输入
   ├─ Claude Code 理解意图
   ├─ 调整播放列表/回答问题
   └─ 返回 3
```

### 对话交互流程

```
用户输入: "我现在心情有点低落，换首歌"
  ↓
对话管理模块: 意图识别 = "调整推荐 + 心情更新"
  ↓
Claude Code Agent:
  ├─ 理解当前场景
  ├─ 分析心情需求（低落）
  ├─ 查询用户音乐历史中适合的歌曲
  ├─ 生成新推荐
  └─ 准备回应
  ↓
音乐推荐引擎: 生成更新后的播放列表
  ↓
系统回应:
  ├─ 聊天界面: "我理解你现在的心情，为你换一些更温暖的歌曲..."
  └─ 播放器: 切换到新歌单
  ↓
反馈记录: 记录这次交互，用于未来优化
```

---

## 技术栈建议

### 后端
- **核心框架**: Python + Trae Agent（基于字节跳动的 trae-agent 项目）
- **Web 框架**: FastAPI（高性能 API）
- **数据库**:
  - PostgreSQL（结构化数据）
  - ChromaDB/Pinecone（向量搜索）
  - Redis（缓存和会话）
- **LLM**: Claude Code API
- **任务队列**: Celery + Redis（异步处理）

### 前端
- **Web**: React + TypeScript
- **UI 组件**: shadcn/ui 或 Ant Design
- **状态管理**: Zustand/Jotai
- **音频播放**: Web Audio API + Howler.js

### 基础设施
- **容器化**: Docker + Docker Compose
- **部署**: Fly.io / Vercel / AWS
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack (Elasticsearch, Logstash, Kibana)

---

## 集成的 Trae Agent 组件

由于我们刚分析了 trae-agent 项目，我们可以利用以下组件来构建 Claudio：

| Trae Agent 组件 | Claudio 中的用途 |
|----------------|-----------------|
| Agent 框架 | 作为 Claudio 的核心智能体框架 |
| 工具系统 | 扩展自定义工具：音乐搜索、歌单管理、设备控制等 |
| LLM 客户端 | 连接 Claude Code API |
| 配置管理 | 管理 Claudio 的配置 |
| 轨迹记录 | 记录用户交互和推荐效果，用于优化 |
| CLI（可选） | 提供开发者调试界面 |

### 自定义工具示例

我们可以基于 Trae Agent 的工具系统创建以下工具：

```python
# 音乐搜索工具
class MusicSearchTool(Tool):
    def get_name(self) -> str:
        return "music_search"
    
    def get_description(self) -> str:
        return "Search for music based on keywords, mood, or characteristics"
    
    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(name="query", type="string", description="Search query"),
            ToolParameter(name="mood", type="string", description="Mood to match", required=False),
            ToolParameter(name="genre", type="string", description="Genre preference", required=False),
        ]
    
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        # 实现音乐搜索
        pass

# 设备控制工具
class DeviceControlTool(Tool):
    def get_name(self) -> str:
        return "device_control"
    
    async def execute(self, arguments: ToolCallArguments) -> ToolExecResult:
        # 实现设备控制
        pass
```

---

## 数据导入和预处理

### 14 年音乐数据导入流程

```
原始数据（各种格式）
  ↓
数据清洗
  ├─ 去重
  ├─ 标准化格式
  └─ 补全元数据
  ↓
特征提取
  ├─ 通过音乐 API 获取音频特征
  ├─ 分析歌单创建场景（基于时间戳推断）
  └─ 向量嵌入生成
  ↓
结构化存储
  ├─ 关系数据库（歌单、歌曲、播放历史）
  └─ 向量数据库（相似度搜索）
  ↓
用户偏好模型训练
  ├─ 分析历史播放数据
  ├─ 计算歌曲偏好权重
  └─ 建立用户音乐画像
```

---

## 开发路线图

### Phase 1: MVP（最小可行产品）
- [ ] 基础音乐播放器
- [ ] 简单聊天界面
- [ ] 音乐数据导入和结构化
- [ ] 集成一个音乐 API（如 Spotify）
- [ ] 基础推荐逻辑
- [ ] Claude Code 集成

### Phase 2: 核心功能完善
- [ ] 场景感知引擎（天气、时间）
- [ ] 多设备支持
- [ ] 个性化推荐优化
- [ ] 对话上下文管理
- [ ] 用户偏好学习

### Phase 3: 高级特性
- [ ] 14 年历史深度分析
- [ ] 心情推断和响应
- [ ] 日程深度集成
- [ ] 可视化音乐推荐理由
- [ ] 社交分享功能

---

## 配置示例

```yaml
# claudio_config.yaml
agents:
  claudio:
    model: claude-3-opus
    max_steps: 100
    enable_lakeview: true
    tools:
      - music_search
      - playlist_management
      - device_control
      - weather_query
      - calendar_query
      - sequentialthinking
      - task_done

model_providers:
  anthropic:
    api_key: your_claude_api_key
    provider: anthropic

integrations:
  music_api:
    spotify:
      client_id: your_spotify_client_id
      client_secret: your_spotify_client_secret
  weather_api:
    openweathermap:
      api_key: your_weather_api_key
  calendar:
    google:
      credentials_path: path/to/google_credentials.json

devices:
  default: "living_room_sonos"
  available:
    - name: "living_room_sonos"
      type: "sonos"
      ip: "192.168.1.100"
    - name: "bedroom_homepod"
      type: "homepod"

data:
  music_history_path: "/path/to/14years_music_data"
```

---

## 总结

Claudio 音乐 AI 代理"z"项目将通过以下方式实现愿景：

1. **基于 Trae Agent 框架**：利用我们刚分析的成熟架构
2. **深度整合 14 年音乐数据**：结构化存储和智能分析
3. **实时场景感知**：天气、日程、心情、时间多维度联动
4. **自然语言交互**：通过聊天界面与用户无缝沟通
5. **设备集成**：连接用户的音响设备，提供完整体验

这个设计将 Claudio 打造成真正的"音乐品味本体"，不仅是一个播放器，更是能理解和主动规划用户音乐体验的智能助手。
