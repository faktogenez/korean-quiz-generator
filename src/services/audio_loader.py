import os
import asyncio
import hashlib
import shutil
import subprocess
import numpy as np
import wave
from edge_tts import Communicate

class AudioLoader:
    def __init__(self, cache_dir: str = "assets/cache", ffmpeg_path: str = "ffmpeg"):
        self.cache_dir = cache_dir
        self.ffmpeg_path = ffmpeg_path
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, text: str, voice: str) -> str:
        text_hash = hashlib.md5(f"{text}|{voice}".encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{text_hash}.mp3")

    async def get_audio(self, text: str, voice: str) -> str:
        """
        Генерирует аудио через edge-tts (с кэшированием).
        Возвращает путь к готовому MP3.
        """
        file_path = self._get_cache_path(text, voice)
        
        if not os.path.exists(file_path):
            communicate = Communicate(text=text, voice=voice)
            await communicate.save(file_path)
            
        return file_path

    def get_duration(self, audio_path: str) -> float:
        """Замеряет длительность через ffprobe."""
        # Проверяем, есть ли ffprobe (обычно в той же папке, что и ffmpeg)
        cmd = [self.ffmpeg_path.replace("ffmpeg", "ffprobe"), "-v", "error", 
               "-show_entries", "format=duration", "-of", 
               "default=noprint_wrappers=1:nokey=1", audio_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    # Здесь можно будет добавить твои генераторы 'generate_timer_audio' и 'generate_ding', 
    # когда начнем собирать видеоряд.