#!/usr/bin/env python3
"""Quick song addition tool for Claudio"""

import json
import os
import sys
from datetime import datetime


def get_next_song_id():
    """Get the next available song ID"""
    songs_dir = os.path.join(os.path.dirname(__file__), "songs")
    max_id = 0
    
    if os.path.exists(songs_dir):
        for filename in os.listdir(songs_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(songs_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    songs_data = json.load(f)
                    for song in songs_data:
                        song_id = song.get('id', '')
                        if song_id.startswith('song_'):
                            try:
                                num = int(song_id.split('_')[1])
                                if num > max_id:
                                    max_id = num
                            except (IndexError, ValueError):
                                continue
    
    return f"song_{max_id + 1}"


def get_input_with_default(prompt, default=""):
    """Get input from user with default value"""
    result = input(f"{prompt} [{default}]: ").strip()
    return result if result else default


def quick_add_song():
    """Interactive song addition"""
    print("=" * 50)
    print("Claudio 歌曲快速添加工具")
    print("=" * 50)
    print()
    
    print("请输入歌曲信息：")
    print()
    
    # Get song data
    song_id = get_next_song_id()
    print(f"自动生成 ID: {song_id}")
    print()
    
    title = get_input_with_default("歌曲名称")
    artist_str = get_input_with_default("歌手 (多个用逗号分隔)")
    album = get_input_with_default("专辑名称", "未知专辑")
    genre_str = get_input_with_default("风格 (多个用逗号分隔, 如: 流行,抒情")
    release_year_str = get_input_with_default("发行年份", str(datetime.now().year))
    duration_str = get_input_with_default("时长 (秒)", "180")
    
    # Parse inputs
    artists = [a.strip() for a in artist_str.split(',')] if artist_str else ["未知歌手"]
    genres = [g.strip() for g in genre_str.split(',')] if genre_str else ["流行"]
    
    try:
        release_year = int(release_year_str)
    except ValueError:
        release_year = datetime.now().year
    
    try:
        duration = int(duration_str)
    except ValueError:
        duration = 180
    
    # Get audio features (optional)
    print()
    print("是否添加音频特征？(可选)")
    print("这些特征会影响推荐结果")
    print()
    
    add_features = get_input_with_default("添加音频特征? (y/n)", "n").lower() == 'y'
    
    features = {}
    if add_features:
        print()
        print("请输入音频特征 (0-1 范围):")
        print()
        
        features['tempo'] = float(get_input_with_default("节奏 (Tempo)", "120"))
        features['energy'] = float(get_input_with_default("能量 (Energy)", "0.5"))
        features['valence'] = float(get_input_with_default("情绪 (Valence)", "0.5"))
        features['danceability'] = float(get_input_with_default("舞蹈性 (Danceability)", "0.5"))
        features['acousticness'] = float(get_input_with_default("声学特性 (Acousticness)", "0.3"))
    
    # Create song data
    song_data = {
        "id": song_id,
        "title": title,
        "artist": artists,
        "album": album,
        "genre": genres,
        "release_year": release_year,
        "duration": duration,
        "features": features
    }
    
    # Show preview
    print()
    print("=" * 50)
    print("歌曲信息预览：")
    print("=" * 50)
    print(json.dumps(song_data, ensure_ascii=False, indent=2))
    print()
    
    confirm = get_input_with_default("确认添加? (y/n)", "y").lower() == 'y'
    
    if confirm:
        # Add to sample_songs.json
        songs_file = os.path.join(os.path.dirname(__file__), "songs", "sample_songs.json")
        
        if os.path.exists(songs_file):
            with open(songs_file, 'r', encoding='utf-8') as f:
                songs_data = json.load(f)
        else:
            songs_data = []
        
        songs_data.append(song_data)
        
        with open(songs_file, 'w', encoding='utf-8') as f:
            json.dump(songs_data, f, ensure_ascii=False, indent=2)
        
        print()
        print("✅ 歌曲添加成功！")
        print()
        print("下一步：")
        print("1. 重启后端服务以导入新歌曲")
        print("2. 或访问前端即可看到新歌曲")
        print()
    else:
        print()
        print("取消添加")
        print()


def batch_add_songs():
    """Batch song addition"""
    print("=" * 50)
    print("批量添加歌曲")
    print("=" * 50)
    print()
    
    print("请准备一个 JSON 文件，格式如下：")
    print()
    print("""
[
  {
    "id": "song_001",
    "title": "歌曲名称",
    "artist": ["歌手"],
    "album": "专辑",
    "genre": ["流行"],
    "release_year": 2024,
    "duration": 180,
    "features": {}
  }
]
""")
    print()
    
    file_path = input("请输入 JSON 文件路径: ").strip()
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_songs = json.load(f)
            
            # Assign IDs if missing
            for song in new_songs:
                if 'id' not in song:
                    song['id'] = get_next_song_id()
            
            # Add to sample_songs.json
            songs_file = os.path.join(os.path.dirname(__file__), "songs", "sample_songs.json")
            
            if os.path.exists(songs_file):
                with open(songs_file, 'r', encoding='utf-8') as f:
                    songs_data = json.load(f)
            else:
                songs_data = []
            
            existing_ids = {s['id'] for s in songs_data}
            
            added_count = 0
            for song in new_songs:
                if song['id'] not in existing_ids:
                    songs_data.append(song)
                    added_count += 1
            
            with open(songs_file, 'w', encoding='utf-8') as f:
                json.dump(songs_data, f, ensure_ascii=False, indent=2)
            
            print()
            print(f"✅ 成功添加 {added_count} 首歌曲！")
            print()
            
        except Exception as e:
            print(f"错误: {e}")
    else:
        print("文件不存在！")


def main():
    """Main function"""
    print()
    print("Claudio 歌曲管理工具")
    print()
    print("1. 快速添加单首歌曲")
    print("2. 批量添加歌曲")
    print("3. 查看现有歌曲")
    print("0. 退出")
    print()
    
    choice = input("请选择操作 (0-3): ").strip()
    
    if choice == "1":
        quick_add_song()
    elif choice == "2":
        batch_add_songs()
    elif choice == "3":
        songs_file = os.path.join(os.path.dirname(__file__), "songs", "sample_songs.json")
        if os.path.exists(songs_file):
            with open(songs_file, 'r', encoding='utf-8') as f:
                songs_data = json.load(f)
            print()
            print(f"现有 {len(songs_data)} 首歌曲:")
            print()
            for i, song in enumerate(songs_data, 1):
                artists = ", ".join(song.get('artist', []))
                print(f"{i}. {song.get('title')} - {artists}")
            print()
    elif choice == "0":
        print("退出！")
        sys.exit(0)
    else:
        print("无效选择！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("用户中断！")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
