# -*- coding: utf-8 -*-
"""
무료 고화질 AI 비주얼 생성 엔진
Pollinations.ai (Flux/SDXL 9:16) 100% 무료 무제한 생성 + 오프라인 대비 블루프린트 비상 폴백
"""

import os
import hashlib
import logging
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List
import requests
from PIL import Image, ImageDraw, ImageFont
from .config import CACHE_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, FONT_PATH

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def create_fallback_blueprint_image(title: str, subtitle: str, output_path: Path):
    """
    네트워크 장애나 외부 오류 시 작동하는 다크 테크놀로지 블루프린트 9:16 배경 생성기
    """
    img = Image.new("RGB", (720, 1280), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    # 1. 그리드 라인 그리기 (공학 도면 느낌)
    for x in range(0, 720, 40):
        draw.line([(x, 0), (x, 1280)], fill=(30, 41, 59), width=1)
    for y in range(0, 1280, 40):
        draw.line([(0, y), (720, y)], fill=(30, 41, 59), width=1)
        
    # 2. 중심 프레임
    draw.rectangle([60, 200, 660, 900], outline=(56, 189, 248), width=3)
    
    # 3. 텍스트 추가
    try:
        font_title = ImageFont.truetype(FONT_PATH, 36)
        font_sub = ImageFont.truetype(FONT_PATH, 24)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        
    draw.text((360, 500), "신비한 건축사전", fill=(255, 215, 0), font=font_title, anchor="mm")
    draw.text((360, 560), title[:20], fill=(255, 255, 255), font=font_sub, anchor="mm")
    draw.text((360, 610), subtitle[:25], fill=(148, 163, 184), font=font_sub, anchor="mm")
    
    img.save(str(output_path), "JPEG", quality=90)

def download_pollinations_image(prompt: str, output_path: Path, width: int = 720, height: int = 1280) -> bool:
    """
    Pollinations.ai 무료 API를 통해 고화질 이미지를 다운로드합니다.
    """
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42"
    
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=25)
        if resp.status_code == 200 and len(resp.content) > 5000:
            output_path.write_bytes(resp.content)
            logger.info(f"AI 이미지 다운로드 성공: {output_path.name}")
            return True
        else:
            logger.warning(f"Pollinations 응답 이상 (status={resp.status_code}, size={len(resp.content)})")
            return False
    except Exception as e:
        logger.warning(f"Pollinations 이미지 다운로드 실패: {e}")
        return False

def generate_scene_image(prompt: str, output_path: Path, fallback_title: str = "건축의 비밀", fallback_sub: str = "공학 분석") -> Path:
    """
    씬별 이미지를 캐시 확인 후 생성하고 파일 경로를 반환합니다.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 캐시 확인 (프롬프트 해시 기반)
    prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    cache_file = CACHE_DIR / f"{prompt_hash}.jpg"
    
    if cache_file.exists():
        output_path.write_bytes(cache_file.read_bytes())
        return output_path
        
    success = download_pollinations_image(prompt, output_path)
    if success:
        cache_file.write_bytes(output_path.read_bytes())
    else:
        logger.info(f"비상 블루프린트 이미지 생성: {output_path.name}")
        create_fallback_blueprint_image(fallback_title, fallback_sub, output_path)
        
    return output_path

def process_episode_visuals(episode: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
    """
    에피소드의 모든 씬에 대해 9:16 비주얼 이미지를 생성합니다.
    """
    output_dir = Path(output_dir)
    scenes = episode.get("scenes", [])
    title = episode.get("title", "신비한 건축사전")
    
    for i, scene in enumerate(scenes):
        scene_img_path = output_dir / f"scene_{i+1:02d}_visual.jpg"
        prompt = scene.get("visual_prompt", f"Architectural mystery {title}, 8k, cinematic, 9:16 vertical")
        subtitle = scene.get("narrator", "")[:20]
        
        generate_scene_image(prompt, scene_img_path, fallback_title=title, fallback_sub=subtitle)
        scene["image_file"] = str(scene_img_path)
        
    # 첫 번째 씬의 이미지를 썸네일로도 지정
    if scenes and "image_file" in scenes[0]:
        episode["thumbnail_file"] = scenes[0]["image_file"]
        
    return episode
