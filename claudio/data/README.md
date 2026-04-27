# Claudio 音乐数据导入指南

欢迎使用 Claudio 音乐代理！这个文档将帮助您导入自己的歌曲数据。

## 目录结构

```
data/
├── songs/          # 歌曲数据目录
│   └── sample_songs.json
├── playlists/      # 播放列表数据目录
│   └── sample_playlists.json
└── history/        # 收听历史数据目录
    └── sample_history.json
```

## 歌曲数据格式

每首歌曲需要包含以下字段：

```json
{
  "id": "song_001",              // 唯一标识符
  "title": "歌曲名称",
  "artist": ["歌手1", "歌手2"], // 歌手数组
  "album": "专辑名称",
  "genre": ["流行", "抒情"],    // 风格数组
  "release_year": 2024,          // 发行年份
  "duration": 258,               // 时长(秒)
  "features": {                   // 音频特征（可选）
    "tempo": 120.0,              // 节奏
    "energy": 0.5,               // 能量(0-1)
    "valence": 0.6,              // 情绪(0-1)
    "danceability": 0.7,         // 舞蹈性(0-1)
    "acousticness": 0.3          // 声学特性(0-1)
  }
}
```

## 快速开始

### 方法一：直接添加到现有文件

1. 编辑 `data/songs/sample_songs.json` 文件
2. 按照格式添加您的歌曲数据
3. 重启后端服务，数据会自动导入

### 方法二：创建新的 JSON 文件

1. 在 `data/songs/` 目录下创建新的 JSON 文件，如 `my_songs.json`
2. 按照上述格式添加歌曲数据
3. 重启后端服务

### 方法三：使用 API 触发导入

启动后端服务后，发送 POST 请求到：

```
POST /api/import-data
```

## 音频特征说明

| 特征 | 说明 | 范围 |
|------|------|------|
| tempo | 每分钟节拍数 | 0-200+ |
| energy | 能量/强度 | 0-1 |
| valence | 情绪(正面/负面) | 0-1 |
| danceability | 舞蹈性 | 0-1 |
| acousticness | 声学特性 | 0-1 |

## 示例数据

更多示例请查看：
- `data/songs/sample_songs.json` - 示例歌曲
- `data/playlists/sample_playlists.json` - 示例播放列表
- `data/history/sample_history.json` - 示例收听历史

## 常见问题

**Q: 我可以不提供音频特征吗？**
A: 可以！features 字段是可选的，如果不提供，会使用默认值。

**Q: 如何确保我的歌曲能被正确推荐？**
A: 填写准确的 genre（风格）和 features（特征）可以让推荐更准确。

**Q: 我可以导入音乐文件吗？**
A: 目前只支持元数据导入，不支持音频文件本身。

## 工具

我们提供了 `quick_add_song.py` 工具来帮助您快速添加歌曲！
