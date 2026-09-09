# -*- coding: utf-8 -*-
"""
FFmpeg & PIL 기반 고품질 숏폼 영상 합성 렌더링 엔진
신비한 건축사전 시그니처 연출:
1. 9:16 (1080x1920) 세로형 최적화
2. 켄 번스(Ken Burns) 카메라 모션 효과
3. 붉은색/노란색 인포그래픽 치수선(↔ 120m), 타겟 링, 수치 오버레이
4. 볼드 고딕 하이라이트 자막 박스
5. 나레이션 음성 + 앰비언트 서스펜스 BGM 자동 믹싱
"""

import os
import wave
import shutil
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from .config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, FONT_PATH, BGM_DIR

logger = logging.getLogger(__name__)
FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

def ensure_bgm_track() -> Path:
    """
    저작권 프리 긴장감/다큐 BGM 트랙이 없으면 절차적 생성하여 저장합니다.
    """
    bgm_file = BGM_DIR / "ambient_tension.wav"
    if bgm_file.exists() and bgm_file.stat().st_size > 10000:
        return bgm_file
        
    logger.info("기본 앰비언트 긴장감 BGM 트랙 생성 중...")
    sample_rate = 44100
    duration = 70  # 최대 70초 분량
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 딥 베이스 패드 (55Hz, 110Hz, 165Hz 조화음)
    pad = 0.12 * np.sin(2 * np.pi * 55 * t) + 0.08 * np.sin(2 * np.pi * 110 * t) + 0.04 * np.sin(2 * np.pi * 165 * t)
    # 은은한 테크 펄스 (1.5초 주기)
    pulse = (np.sin(2 * np.pi * 0.67 * t) > 0.6) * 0.04 * np.sin(2 * np.pi * 220 * t)
    # 페이드 인 (2초), 페이드 아웃 (4초)
    fade_in = np.clip(t / 2.0, 0, 1)
    fade_out = np.clip((duration - t) / 4.0, 0, 1)
    envelope = fade_in * fade_out
    
    audio = ((pad + pulse) * envelope * 32767).astype(np.int16)
    with wave.open(str(bgm_file), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
        
    return bgm_file

def composite_scene_frame(
    raw_img_path: Path,
    category: str,
    infographic: Dict[str, Any],
    narrator_text: str,
    output_path: Path,
    scene_type: str = "hook"
) -> Path:
    """
    PIL을 이용해 원본 이미지 위에 신비한 건축사전 특유의 인포그래픽, 헤더 배지, 자막을 합성합니다.
    """
    output_path = Path(output_path)
    W, H = VIDEO_WIDTH, VIDEO_HEIGHT
    
    # 1. 배경 이미지 로드 및 1080x1920 센터 크롭 스케일링
    try:
        base_img = Image.open(str(raw_img_path)).convert("RGB")
    except Exception:
        base_img = Image.new("RGB", (W, H), color=(15, 23, 42))
        
    # 종횡비 유지하면서 1080x1920 채우기
    img_w, img_h = base_img.size
    scale = max(W / img_w, H / img_h)
    new_w, new_h = int(img_w * scale), int(img_h * scale)
    base_img = base_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - W) // 2
    top = (new_h - H) // 2
    frame = base_img.crop((left, top, left + W, top + H))
    draw = ImageDraw.Draw(frame)
    
    # 2. 상/하단 그라데이션 비네팅 (가독성 향상)
    top_overlay = Image.new("RGBA", (W, 280), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(top_overlay)
    for y in range(280):
        alpha = int((1 - y / 280) * 160)
        t_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    frame.paste(top_overlay, (0, 0), top_overlay)
    
    bot_overlay = Image.new("RGBA", (W, 500), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(bot_overlay)
    for y in range(500):
        alpha = int((y / 500) * 180)
        b_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    frame.paste(bot_overlay, (0, H - 500), bot_overlay)
    
    # 3. 폰트 로드
    try:
        font_badge = ImageFont.truetype(FONT_PATH, 34)
        font_dim = ImageFont.truetype(FONT_PATH, 44)
        font_label = ImageFont.truetype(FONT_PATH, 30)
        font_sub = ImageFont.truetype(FONT_PATH, 48)
    except Exception:
        font_badge = font_dim = font_label = font_sub = ImageFont.load_default()

    # 4. 상단 헤더 배지 (#신비한건축사전 | 분야)
    badge_str = f" #신비한건축사전  |  {category} "
    draw.rounded_rectangle([200, 150, 880, 225], radius=35, fill=(15, 23, 42), outline=(255, 215, 0), width=3)
    draw.text((540, 187), badge_str, font=font_badge, fill=(255, 255, 255), anchor="mm")
    
    # 5. 인포그래픽 연출 (타겟 링 & 치수선 & 수치 박스)
    info_label = infographic.get("label", "공학 구조 분석")
    info_dim = infographic.get("dimension", "핵심 원리")
    
    # 타겟 위치 좌표
    cx, cy = 540, 800
    reticle_color = (255, 59, 48) if scene_type in ["hook", "problem"] else (56, 189, 248) # 레드 or 사이언
    
    # 타겟 원형 링
    r = 110
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=reticle_color, width=4)
    draw.line([(cx - r - 25, cy), (cx + r + 25, cy)], fill=reticle_color, width=3)
    draw.line([(cx, cy - r - 25), (cx, cy + r + 25)], fill=reticle_color, width=3)
    
    # 연결 치수선 및 수치 박스
    draw.line([(cx, cy + r), (cx, cy + r + 60)], fill=reticle_color, width=3)
    box_w, box_h = 460, 110
    box_left = cx - box_w // 2
    box_top = cy + r + 60
    draw.rounded_rectangle([box_left, box_top, box_left + box_w, box_top + box_h], radius=15, fill=(15, 15, 20), outline=reticle_color, width=3)
    draw.text((cx, box_top + 32), info_label, font=font_label, fill=reticle_color, anchor="mm")
    draw.text((cx, box_top + 78), f"↔ {info_dim}", font=font_dim, fill=(255, 215, 0), anchor="mm")
    
    # 6. 하단 볼드 자막 박스 (스마트 2줄 줄바꿈)
    words = narrator_text.strip().split()
    lines = []
    curr = ""
    for w in words:
        if len(curr + " " + w) <= 16:
            curr = (curr + " " + w).strip()
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)
    clean_sub = "\n".join(lines[:2])
            
    sub_top = 1430
    draw.rounded_rectangle([70, sub_top, 1010, sub_top + 180], radius=25, fill=(10, 10, 15), outline=(255, 255, 255), width=3)
    draw.text((540, sub_top + 90), clean_sub, font=font_sub, fill=(255, 255, 255), anchor="mm", align="center")
    
    frame.save(str(output_path), "JPEG", quality=95)
    return output_path

def composite_3split_scene_frame(
    raw_img_path: Path,
    category: str,
    infographic: Dict[str, Any],
    narrator_text: str,
    output_path: Path,
    scene_type: str = "problem",
    adjacent_img_paths: List[Path] = None
) -> Path:
    """
    한 이미지 안에 3장의 영상 컷씬(상단: 광각 전경, 중앙: 공학 단면 및 치수선 타겟, 하단: 물리 메커니즘 해석)을
    신비한 건축사전 특유의 다큐멘터리 스타일로 3분할 합성합니다.
    """
    output_path = Path(output_path)
    W, H = VIDEO_WIDTH, VIDEO_HEIGHT
    
    frame = Image.new("RGB", (W, H), color=(10, 14, 23))
    draw = ImageDraw.Draw(frame)
    
    # 폰트 로드
    try:
        font_badge = ImageFont.truetype(FONT_PATH, 32)
        font_cam = ImageFont.truetype(FONT_PATH, 22)
        font_dim = ImageFont.truetype(FONT_PATH, 42)
        font_label = ImageFont.truetype(FONT_PATH, 26)
        font_sub = ImageFont.truetype(FONT_PATH, 48)
    except Exception:
        font_badge = font_cam = font_dim = font_label = font_sub = ImageFont.load_default()

    # 이미지 소스 준비 (주변 씬 이미지 활용 또는 다각도 크롭)
    def load_or_fallback(path: Path, target_w: int, target_h: int, crop_bias: str = "center") -> Image.Image:
        try:
            im = Image.open(str(path)).convert("RGB")
        except Exception:
            im = Image.new("RGB", (target_w, target_h), color=(20, 30, 48))
            
        iw, ih = im.size
        scale = max(target_w / iw, target_h / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        
        left = (nw - target_w) // 2
        if crop_bias == "top":
            top = 0
        elif crop_bias == "bottom":
            top = nh - target_h
        else:
            top = (nh - target_h) // 2
        return im.crop((left, top, left + target_w, top + target_h))

    img1_path = adjacent_img_paths[0] if adjacent_img_paths and len(adjacent_img_paths) > 0 else raw_img_path
    img2_path = raw_img_path
    img3_path = adjacent_img_paths[1] if adjacent_img_paths and len(adjacent_img_paths) > 1 else raw_img_path

    panel1_img = load_or_fallback(img1_path, 960, 460, "top")
    panel2_img = load_or_fallback(img2_path, 960, 560, "center")
    panel3_img = load_or_fallback(img3_path, 960, 340, "bottom")

    # 1. 상단 공식 헤더 배지 (#신비한건축사전 | 분야)
    badge_str = f" #신비한건축사전  |  {category} "
    draw.rounded_rectangle([200, 110, 880, 185], radius=35, fill=(15, 23, 42), outline=(255, 215, 0), width=3)
    draw.text((540, 147), badge_str, font=font_badge, fill=(255, 255, 255), anchor="mm")

    # 2. 패널 1 (상단: 광각 전경 컷씬, y=200~660)
    frame.paste(panel1_img, (60, 200))
    draw.rectangle([60, 200, 1020, 660], outline=(51, 65, 85), width=2)
    # HUD 배지
    draw.rounded_rectangle([75, 215, 340, 255], radius=8, fill=(15, 23, 42), outline=(56, 189, 248), width=2)
    draw.text((207, 235), "● CAM 01 : 광각 전경 관측", font=font_cam, fill=(56, 189, 248), anchor="mm")

    # 3. 패널 2 (중앙: 공학 구조 단면 & 치수선 오버레이, y=680~1240)
    frame.paste(panel2_img, (60, 680))
    reticle_col = (255, 59, 48) if scene_type in ["hook", "problem"] else (56, 189, 248)
    draw.rectangle([60, 680, 1020, 1240], outline=reticle_col, width=3)
    # HUD 배지
    draw.rounded_rectangle([75, 695, 360, 735], radius=8, fill=(15, 23, 42), outline=reticle_col, width=2)
    draw.text((217, 715), "● CAM 02 : 핵심 구조 단면도해", font=font_cam, fill=reticle_col, anchor="mm")

    # 중앙 타겟 레티클 & 치수선 박스
    cx, cy = 540, 920
    r = 85
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=reticle_col, width=3)
    draw.line([(cx - r - 20, cy), (cx + r + 20, cy)], fill=reticle_col, width=2)
    draw.line([(cx, cy - r - 20), (cx, cy + r + 20)], fill=reticle_col, width=2)

    info_label = infographic.get("label", "핵심 공학 구조")
    info_dim = infographic.get("dimension", "원리 분석")
    box_w, box_h = 440, 100
    b_left = cx - box_w // 2
    b_top = 1110
    draw.rounded_rectangle([b_left, b_top, b_left + box_w, b_top + box_h], radius=12, fill=(12, 16, 26), outline=reticle_col, width=3)
    draw.text((cx, b_top + 28), info_label, font=font_label, fill=reticle_col, anchor="mm")
    draw.text((cx, b_top + 70), f"↔ {info_dim}", font=font_dim, fill=(255, 215, 0), anchor="mm")

    # 4. 패널 3 (하단: 미시 디테일 & 시뮬레이션, y=1260~1600)
    frame.paste(panel3_img, (60, 1260))
    draw.rectangle([60, 1260, 1020, 1600], outline=(51, 65, 85), width=2)
    # HUD 배지
    draw.rounded_rectangle([75, 1275, 340, 1315], radius=8, fill=(15, 23, 42), outline=(16, 185, 129), width=2)
    draw.text((207, 1295), "● CAM 03 : 메커니즘 해석", font=font_cam, fill=(16, 185, 129), anchor="mm")

    # 5. 하단 볼드 자막 박스 (스마트 2줄 줄바꿈)
    words = narrator_text.strip().split()
    lines = []
    curr = ""
    for w in words:
        if len(curr + " " + w) <= 16:
            curr = (curr + " " + w).strip()
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)
    clean_sub = "\n".join(lines[:2])

    sub_top = 1630
    draw.rounded_rectangle([70, sub_top, 1010, sub_top + 180], radius=25, fill=(10, 10, 15), outline=(255, 255, 255), width=3)
    draw.text((540, sub_top + 90), clean_sub, font=font_sub, fill=(255, 255, 255), anchor="mm", align="center")

    frame.save(str(output_path), "JPEG", quality=95)
    return output_path

def render_scene_video(frame_img_path: Path, audio_path: Path, duration: float, output_video_path: Path) -> bool:
    """
    합성된 이미지와 음성을 결합하여 켄 번스(미세 줌인) 효과가 적용된 씬 MP4를 렌더링합니다.
    """
    frame_img_path = str(frame_img_path)
    audio_path = str(audio_path)
    output_video_path = str(output_video_path)
    
    # 30fps 기준 총 프레임 수
    total_frames = max(30, int(duration * VIDEO_FPS))
    
    # 부드러운 켄 번스 줌인 필터 (1.0배 -> 1.08배)
    vf_filter = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"zoompan=z='min(zoom+0.0005,1.08)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
    )
    
    cmd = [
        FFMPEG_BIN, "-y",
        "-loop", "1",
        "-i", frame_img_path,
        "-i", audio_path,
        "-t", f"{duration:.2f}",
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_video_path
    ]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"Zoompan 필터 실패, 정적 렌더링으로 폴백: {e}")
        fallback_cmd = [
            FFMPEG_BIN, "-y",
            "-loop", "1",
            "-i", frame_img_path,
            "-i", audio_path,
            "-t", f"{duration:.2f}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_video_path
        ]
        subprocess.run(fallback_cmd, capture_output=True, check=True)
        return True

def stitch_episode_video(
    scene_video_paths: List[Path],
    bgm_path: Path,
    final_output_path: Path,
    temp_dir: Path
) -> Path:
    """
    생성된 4개의 씬 영상을 하나로 병합하고 배경음악(BGM)을 믹싱하여 최종 MP4를 완성합니다.
    """
    final_output_path = Path(final_output_path)
    temp_dir = Path(temp_dir)
    concat_list_file = temp_dir / "concat_list.txt"
    
    # FFmpeg concat list 작성 (Windows 역슬래시 처리)
    lines = [f"file '{Path(p).resolve().as_posix()}'" for p in scene_video_paths]
    concat_list_file.write_text("\n".join(lines), encoding="utf-8")
    
    intermediate_stitched = temp_dir / "stitched_temp.mp4"
    
    # 1. 씬 비디오 무손실 병합
    cmd_concat = [
        FFMPEG_BIN, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(intermediate_stitched)
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)
    
    # 2. 배경음악(BGM) 은은하게 믹싱 (볼륨 10%, 나레이션 100%)
    cmd_mix = [
        FFMPEG_BIN, "-y",
        "-i", str(intermediate_stitched),
        "-stream_loop", "-1",
        "-i", str(bgm_path),
        "-filter_complex", "[1:a]volume=0.10[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(final_output_path)
    ]
    
    try:
        subprocess.run(cmd_mix, capture_output=True, check=True)
    except Exception as e:
        logger.warning(f"BGM 믹싱 실패, 원본 오디오 유지: {e}")
        shutil.copy2(intermediate_stitched, final_output_path)
        
    return final_output_path

def render_full_episode(episode: Dict[str, Any], output_dir: Path, visual_style: str = "hybrid") -> Path:
    """
    에피소드의 전체 렌더링 파이프라인(프레임 합성 -> 씬 렌더링 -> 최종 병합 및 BGM 믹싱)을 실행합니다.
    visual_style:
      - 'hybrid': Hook(풀스크린) -> Problem(3분할 컷씬) -> Solution(3분할 컷씬) -> Punchline(풀스크린)
      - '3split': 전체 씬 3분할 컷씬
      - 'fullscreen': 클래식 단일 풀스크린
    """
    output_dir = Path(output_dir)
    scenes = episode.get("scenes", [])
    category = episode.get("category", "건축 공학")
    ep_id = episode.get("id", "episode")
    
    bgm_path = ensure_bgm_track()
    scene_videos = []
    
    # 3분할 컷씬을 위한 전체 씬 이미지 수집
    all_scene_imgs = [Path(sc.get("image_file")) for sc in scenes if sc.get("image_file")]
    
    for i, sc in enumerate(scenes):
        raw_img = Path(sc.get("image_file"))
        audio_file = Path(sc.get("audio_file"))
        duration = sc.get("duration", 5.0)
        scene_type = sc.get("type", "hook")
        infographic = sc.get("infographic", {})
        narrator = sc.get("narrator", "")
        
        # 3분할 컷씬 적용 여부 판별
        use_3split = (visual_style == "3split") or (visual_style == "hybrid" and scene_type in ["problem", "solution"])
        composite_path = output_dir / f"scene_{i+1:02d}_composite.jpg"
        
        if use_3split:
            # 타 씬 이미지들을 인접 패널 소스로 활용
            adj_imgs = [img for idx, img in enumerate(all_scene_imgs) if idx != i]
            composite_3split_scene_frame(
                raw_img, category, infographic, narrator, composite_path,
                scene_type=scene_type, adjacent_img_paths=adj_imgs
            )
            logger.info(f"[{ep_id}] Scene {i+1} 3분할 다각도 컷씬 합성 완료")
        else:
            composite_scene_frame(raw_img, category, infographic, narrator, composite_path, scene_type)
            logger.info(f"[{ep_id}] Scene {i+1} 시그니처 풀스크린 프레임 합성 완료")
        
        # 2. 씬별 비디오 렌더링
        scene_video_path = output_dir / f"scene_{i+1:02d}_rendered.mp4"
        render_scene_video(composite_path, audio_file, duration, scene_video_path)
        scene_videos.append(scene_video_path)
        logger.info(f"[{ep_id}] Scene {i+1} 비디오 렌더링 완료")
        
    # 3. 최종 완성본 병합
    final_video_path = output_dir / f"{ep_id}_final.mp4"
    stitch_episode_video(scene_videos, bgm_path, final_video_path, output_dir)
    episode["final_video"] = str(final_video_path)
    logger.info(f"[{ep_id}] 최종 숏폼 완성: {final_video_path}")
    
    return final_video_path
