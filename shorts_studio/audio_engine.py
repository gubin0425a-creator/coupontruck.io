# -*- coding: utf-8 -*-
"""
Edge-TTS 기반 고품질 한국어 음성 합성 엔진
100% 무료, 무제한, 0 API 크레딧으로 신뢰감 있는 전문 성우 나레이션 생성 및 타이밍 산출
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import edge_tts
from moviepy.editor import AudioFileClip
from .config import DEFAULT_VOICE

logger = logging.getLogger(__name__)

async def generate_audio_clip(text: str, output_path: Path, voice: str = DEFAULT_VOICE) -> float:
    """
    단일 텍스트에 대한 음성 MP3를 생성하고 정확한 재생 시간(초)을 반환합니다.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    
    try:
        clip = AudioFileClip(str(output_path))
        duration = clip.duration
        clip.close()
    except Exception as e:
        logger.warning(f"오디오 길이 측정 예외, 기본값 계산: {e}")
        # 한국어 글자당 약 0.15초 추정
        duration = max(2.5, len(text) * 0.15)
        
    return duration

def generate_srt_file(scenes: List[Dict[str, Any]], srt_path: Path):
    """
    씬별 텍스트와 타이밍을 기반으로 자막 SRT 파일을 생성합니다.
    """
    srt_path = Path(srt_path)
    srt_lines = []
    current_time = 0.0
    
    def format_srt_time(seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    for idx, sc in enumerate(scenes, start=1):
        duration = sc.get("duration", 4.0)
        start_str = format_srt_time(current_time)
        end_time = current_time + duration
        end_str = format_srt_time(end_time)
        text = sc.get("narrator", "")
        
        # 긴 문장은 2줄로 분할
        if len(text) > 22:
            mid = len(text) // 2
            split_idx = text.rfind(" ", 0, mid + 5)
            if split_idx != -1:
                text = text[:split_idx] + "\n" + text[split_idx+1:]
                
        srt_lines.append(f"{idx}\n{start_str} --> {end_str}\n{text}\n")
        current_time = end_time
        
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")

async def process_episode_audio(episode: Dict[str, Any], output_dir: Path, voice: str = DEFAULT_VOICE) -> Dict[str, Any]:
    """
    에피소드의 모든 씬에 대한 음성을 생성하고 자막을 빌드합니다.
    """
    output_dir = Path(output_dir)
    scenes = episode.get("scenes", [])
    total_duration = 0.0
    
    for i, scene in enumerate(scenes):
        scene_audio_path = output_dir / f"scene_{i+1:02d}_audio.mp3"
        text = scene.get("narrator", "")
        duration = await generate_audio_clip(text, scene_audio_path, voice=voice)
        
        scene["audio_file"] = str(scene_audio_path)
        scene["duration"] = duration
        total_duration += duration
        logger.info(f"Scene {i+1} 음성 생성 완료: {duration:.2f}s")
        
    srt_path = output_dir / "subtitles.srt"
    generate_srt_file(scenes, srt_path)
    episode["srt_file"] = str(srt_path)
    episode["total_duration"] = total_duration
    
    return episode
