# Claudio - 智能音乐代理

Claudio 是一个基于 AI 的音乐代理，通过结合 14 年的音乐数据（3000+ 歌单）、实时天气、日程和心情信息，为用户提供 24 小时个性化电台服务。

## 核心功能

- **个性化推荐**: 根据用户历史歌单和实时场景（如周一晚上）推荐音乐
- **多维度联动**: 前端为播放器 + 聊天界面，后端连接音响设备、音乐 API 和 Claude Code
- **动态调整**: 用户可随时通过聊天界面与 Claudio 互动，调整歌单或获取音乐推荐

## 技术栈

### 后端
- Python 3.12+
- FastAPI
- Anthropic Claude API
- SQLAlchemy (数据库)
- ChromaDB (向量搜索)
- Redis (缓存和任务队列)

### 前端
- React 18
- Vite
- Howler.js (音频播放)
- Lucide React (图标)

## 项目结构

```
├── claudio/              # 后端代码
│   ├── core/             # 核心模块
│   ├── config/           # 配置管理
│   ├── data/             # 数据导入和处理
│   ├── integrations/     # 外部服务集成
│   ├── models/           # 数据库模型
│   ├── utils/            # 工具函数
│   ├── main.py           # 主应用入口
│   └── pyproject.toml    # 项目配置
├── frontend/             # 前端代码
│   ├── public/           # 静态资源
│   ├── src/              # 源代码
│   ├── package.json      # 前端依赖
│   └── vite.config.js    # Vite 配置
└── README.md             # 项目说明
```

## 快速开始

### 后端设置

1. **安装依赖**
   ```bash
   cd claudio
   pip install -e .
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入 API 密钥
   ```

3. **启动后端服务**
   ```bash
   cd claudio
   python main.py
   ```
   服务将在 http://localhost:8000 运行

### 前端设置

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动前端开发服务器**
   ```bash
   cd frontend
   npm run dev
   ```
   前端将在 http://localhost:3000 运行

## API 端点

- `POST /api/recommend` - 获取音乐推荐
- `POST /api/chat` - 与 Claudio 聊天
- `POST /api/generate-playlist-name` - 生成播放列表名称
- `GET /api/context` - 获取当前场景上下文
- `POST /api/import-data` - 导入音乐数据
- `GET /api/devices` - 获取可用设备列表
- `POST /api/devices/connect` - 连接设备
- `POST /api/devices/disconnect` - 断开设备连接
- `POST /api/devices/play` - 播放音乐
- `POST /api/devices/pause` - 暂停音乐
- `POST /api/devices/stop` - 停止音乐
- `POST /api/devices/volume` - 设置音量
- `GET /api/devices/status` - 获取设备状态

## 数据导入

1. **准备数据**
   - 将音乐数据放入 `claudio/data/songs/` 目录
   - 将歌单数据放入 `claudio/data/playlists/` 目录
   - 将收听历史放入 `claudio/data/history/` 目录

2. **导入数据**
   - 访问 `http://localhost:8000/api/import-data` 或
   - 运行 `python -m data.data_importer`

## 示例数据

项目包含示例数据，位于 `claudio/data/` 目录下，可以直接用于测试。

## 许可证

MIT
