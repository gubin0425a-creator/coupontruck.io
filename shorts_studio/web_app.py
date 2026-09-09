# -*- coding: utf-8 -*-
"""
신비한 건축사전 원클릭 풀 자동화 프로그램 로컬 웹 서버 (FastAPI)
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .config import BASE_DIR, OUTPUT_DIR, DEFAULT_VOICE, VOICE_OPTIONS, DEFAULT_BATCH_COUNT
from .pipeline import run_batch_pipeline, progress_state
from .youtube_uploader import upload_and_schedule_video
from .assets.templates.wonka_playbook import get_playbook_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ShortsStudioWeb")

app = FastAPI(title="WonkaShorts Studio - 원카 숏츠 스튜디오")

# 정적 파일 마운트 (UI 및 비디오 스트리밍)
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

class BatchRequest(BaseModel):
    theme: str = "신비한 세계 건축과 토목의 비밀"
    count: int = DEFAULT_BATCH_COUNT
    voice: str = DEFAULT_VOICE
    api_key: Optional[str] = None
    visual_style: str = "hybrid" # 'hybrid' (3분할 컷씬 포함), '3split', 'fullscreen'

class UploadRequest(BaseModel):
    batch_id: str
    ep_ids: Optional[list] = None

@app.get("/")
async def get_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return JSONResponse({"message": "Shorts Studio API Running. static/index.html is loading..."})
    return FileResponse(str(index_file))

@app.get("/api/playbook")
async def get_playbook():
    """원카AI 영상 분석 조언 및 숏폼 제작 바이블 반환"""
    return get_playbook_data()

@app.get("/api/config")
async def get_config():
    return {
        "voices": VOICE_OPTIONS,
        "default_voice": DEFAULT_VOICE,
        "default_count": DEFAULT_BATCH_COUNT,
        "is_running": progress_state.is_running
    }

@app.get("/api/status")
async def get_status():
    return {
        "is_running": progress_state.is_running,
        "current_step": progress_state.current_step,
        "percent": progress_state.percent,
        "current_batch_id": progress_state.current_batch_id,
        "completed_episodes": progress_state.completed_episodes,
        "total_episodes": progress_state.total_episodes,
        "error": progress_state.error,
        "has_manifest": bool(progress_state.manifest)
    }

def run_async_batch(theme: str, count: int, voice: str, api_key: str, visual_style: str = "hybrid"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_batch_pipeline(
        theme=theme, count=count, voice=voice, api_key=api_key, visual_style=visual_style
    ))

@app.post("/api/start_batch")
async def start_batch(req: BatchRequest, background_tasks: BackgroundTasks):
    if progress_state.is_running:
        raise HTTPException(status_code=400, detail="이미 대량 제작 작업이 진행 중입니다.")
    
    background_tasks.add_task(
        run_async_batch, req.theme, req.count, req.voice, req.api_key, req.visual_style
    )
    return {"status": "started", "message": f"30일치({req.count}편, 스타일: {req.visual_style}) 일괄 제작이 시작되었습니다."}

@app.get("/api/batches")
async def list_batches():
    batches = []
    if OUTPUT_DIR.exists():
        for item in sorted(OUTPUT_DIR.iterdir(), reverse=True):
            if item.is_dir() and item.name.startswith("batch_"):
                manifest_file = item / "schedule_manifest.json"
                csv_file = item / "youtube_batch_schedule.csv"
                ep_count = len(list(item.glob("ep_*")))
                batches.append({
                    "batch_id": item.name,
                    "date": item.name.replace("batch_", ""),
                    "episode_count": ep_count,
                    "has_manifest": manifest_file.exists(),
                    "has_csv": csv_file.exists()
                })
    return {"batches": batches}

@app.get("/api/batch/{batch_id}")
async def get_batch_detail(batch_id: str):
    batch_dir = OUTPUT_DIR / batch_id
    if not batch_dir.exists():
        raise HTTPException(status_code=404, detail="해당 배치를 찾을 수 없습니다.")
        
    manifest_file = batch_dir / "schedule_manifest.json"
    if manifest_file.exists():
        try:
            data = json.loads(manifest_file.read_text(encoding="utf-8"))
            # 상대 URL 변환 for 비디오 플레이어
            for ep in data.get("episodes", []):
                if ep.get("final_video"):
                    ep["video_url"] = f"/output/{batch_id}/{Path(ep['final_video']).parent.name}/{Path(ep['final_video']).name}"
                if ep.get("thumbnail_file"):
                    ep["thumbnail_url"] = f"/output/{batch_id}/{Path(ep['thumbnail_file']).parent.name}/{Path(ep['thumbnail_file']).name}"
            return data
        except Exception as e:
            logger.error(f"Manifest 파싱 오류: {e}")
            
    return {"batch_id": batch_id, "episodes": []}

@app.get("/api/download_csv/{batch_id}")
async def download_csv(batch_id: str):
    csv_file = OUTPUT_DIR / batch_id / "youtube_batch_schedule.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV 파일이 없습니다.")
    return FileResponse(str(csv_file), filename=f"youtube_schedule_{batch_id}.csv", media_type="text/csv")

@app.post("/api/schedule_upload")
async def schedule_upload(req: UploadRequest):
    batch_dir = OUTPUT_DIR / req.batch_id
    manifest_file = batch_dir / "schedule_manifest.json"
    if not manifest_file.exists():
        raise HTTPException(status_code=404, detail="스케줄 매니페스트를 찾을 수 없습니다.")
        
    data = json.loads(manifest_file.read_text(encoding="utf-8"))
    episodes = data.get("episodes", [])
    
    upload_results = []
    for ep in episodes:
        if req.ep_ids and ep.get("id") not in req.ep_ids:
            continue
            
        video_path = ep.get("final_video")
        if not video_path or not Path(video_path).exists():
            continue
            
        seo = ep.get("seo", {})
        title = seo.get("selected_title", ep.get("title", ""))
        desc = seo.get("description", "")
        tags = seo.get("tags", [])
        sched_time = ep.get("schedule", {}).get("scheduled_utc_iso", "")
        
        res = upload_and_schedule_video(
            video_path=Path(video_path),
            title=title,
            description=desc,
            tags=tags,
            publish_at_utc_iso=sched_time
        )
        upload_results.append({"id": ep.get("id"), "title": title, "result": res})
        
    return {"batch_id": req.batch_id, "results": upload_results}
