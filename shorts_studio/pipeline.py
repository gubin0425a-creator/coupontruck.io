# -*- coding: utf-8 -*-
"""
신비한 건축사전 숏폼 30일치(14편) 원클릭 대량 제작 통합 파이프라인
"""

import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from .config import OUTPUT_DIR, DEFAULT_BATCH_COUNT, DEFAULT_VOICE
from .script_engine import generate_batch_scripts
from .seo_engine import build_seo_pack
from .audio_engine import process_episode_audio
from .visual_engine import process_episode_visuals
from .render_engine import render_full_episode
from .schedule_engine import export_batch_schedule_manifest

logger = logging.getLogger(__name__)

class PipelineProgress:
    def __init__(self):
        self.is_running = False
        self.current_step = ""
        self.total_episodes = 0
        self.completed_episodes = 0
        self.percent = 0
        self.current_batch_id = ""
        self.error = None
        self.episodes = []
        self.manifest = {}

    def update(self, step: str, percent: int, current_ep: int = 0, total_ep: int = 0):
        self.current_step = step
        self.percent = percent
        if current_ep:
            self.completed_episodes = current_ep
        if total_ep:
            self.total_episodes = total_ep
        logger.info(f"[{percent}%] {step}")

progress_state = PipelineProgress()

async def run_batch_pipeline(
    theme: str = "신비한 세계 건축과 토목의 비밀",
    count: int = DEFAULT_BATCH_COUNT,
    voice: str = DEFAULT_VOICE,
    api_key: str = None,
    visual_style: str = "hybrid",
    progress_callback: Optional[Callable[[str, int], None]] = None
) -> Dict[str, Any]:
    """
    한 번의 호출로 30일치(14편) 에피소드를 완전 자동 제작합니다.
    visual_style: 'hybrid' (3분할 컷씬 + 풀스크린 믹스), '3split', 'fullscreen'
    """
    global progress_state
    progress_state.is_running = True
    progress_state.error = None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = OUTPUT_DIR / f"batch_{timestamp}"
    batch_dir.mkdir(parents=True, exist_ok=True)
    progress_state.current_batch_id = batch_dir.name
    
    def report(msg: str, pct: int, cur: int = 0, tot: int = count):
        progress_state.update(msg, pct, cur, tot)
        if progress_callback:
            progress_callback(msg, pct)

    try:
        # 1. 14개 에피소드 대본 및 서사 생성
        report(f"30일치({count}편) 4단 서사 대본 및 기획안 생성 중...", 10)
        raw_episodes = generate_batch_scripts(theme=theme, count=count, api_key=api_key)
        
        # 2. 각 에피소드별 100점 SEO 패키지 완성
        report("유튜브 알고리즘 100점 SEO 메타데이터(제목3종, 500자태그, 설명란, 고정댓글) 세팅 중...", 20)
        processed_episodes = []
        for ep in raw_episodes:
            ep["seo"] = build_seo_pack(ep)
            processed_episodes.append(ep)
            
        # 3. 에피소드별 제작 루프 (음성 -> 비주얼 -> 렌더링)
        total_eps = len(processed_episodes)
        final_episodes = []
        
        for idx, ep in enumerate(processed_episodes, start=1):
            ep_id = ep.get("id", f"ep_{idx:02d}")
            ep_dir = batch_dir / f"ep_{idx:02d}_{ep_id}"
            ep_dir.mkdir(parents=True, exist_ok=True)
            
            # Step A: Edge-TTS 나레이션 음성 & 자막 싱크 (무료)
            pct_base = 20 + int((idx - 1) / total_eps * 70)
            report(f"[{idx}/{total_eps}] '{ep['title']}' Edge-TTS 성우 음성 합성 중...", pct_base + 5, idx, total_eps)
            ep = await process_episode_audio(ep, ep_dir, voice=voice)
            
            # Step B: Pollinations AI 9:16 비주얼 생성 (무료)
            report(f"[{idx}/{total_eps}] '{ep['title']}' 9:16 AI 비주얼 생성 중...", pct_base + 12, idx, total_eps)
            ep = process_episode_visuals(ep, ep_dir)
            
            # Step C: FFmpeg 3분할 컷씬 + 켄번스 모션 + 인포그래픽 + 볼드자막 + BGM 믹싱
            report(f"[{idx}/{total_eps}] '{ep['title']}' 신비한 건축사전 3분할 컷씬 비디오 렌더링 중...", pct_base + 20, idx, total_eps)
            render_full_episode(ep, ep_dir, visual_style=visual_style)
            
            final_episodes.append(ep)
            
        # 4. 30일치 주 3회(월, 수, 금 18:00) 스케줄링 및 CSV 매니페스트 출력
        report("30일치(월/수/금 18:00) 스케줄링 및 유튜브용 CSV 매니페스트 생성 중...", 95)
        manifest = export_batch_schedule_manifest(final_episodes, batch_dir)
        
        progress_state.episodes = final_episodes
        progress_state.manifest = manifest
        report("30일치 숏폼 대량 제작 및 100점 SEO 자동 세팅 완료!", 100, total_eps, total_eps)
        
        return manifest
        
    except Exception as e:
        logger.error(f"대량 제작 파이프라인 중단: {e}", exc_info=True)
        progress_state.error = str(e)
        report(f"오류 발생: {e}", 0)
        raise e
    finally:
        progress_state.is_running = False
