# -*- coding: utf-8 -*-
"""
30일치 주 3회(월, 수, 금) 유튜브 자동 예약 스케줄링 및 CSV 매니페스트 엔진
"""

import csv
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from .config import DEFAULT_SCHEDULE_DAYS, DEFAULT_PUBLISH_HOUR

logger = logging.getLogger(__name__)

DAY_INDEX_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

def generate_schedule_dates(
    count: int = 14,
    start_date: datetime = None,
    schedule_days: List[str] = DEFAULT_SCHEDULE_DAYS,
    publish_hour: int = DEFAULT_PUBLISH_HOUR
) -> List[datetime]:
    """
    주 3회(월, 수, 금 18:00) 규칙에 맞추어 향후 30일간의 업로드 예약 날짜 목록을 생성합니다.
    """
    if start_date is None:
        start_date = datetime.now() + timedelta(days=1)
        
    target_weekdays = [DAY_INDEX_MAP[d] for d in schedule_days if d in DAY_INDEX_MAP]
    if not target_weekdays:
        target_weekdays = [0, 2, 4]  # 기본값: 월, 수, 금
        
    scheduled_datetimes = []
    current_dt = start_date.replace(hour=publish_hour, minute=0, second=0, microsecond=0)
    
    while len(scheduled_datetimes) < count:
        if current_dt.weekday() in target_weekdays:
            scheduled_datetimes.append(current_dt)
        current_dt += timedelta(days=1)
        
    return scheduled_datetimes

def export_batch_schedule_manifest(
    episodes: List[Dict[str, Any]],
    output_dir: Path,
    start_date: datetime = None
) -> Dict[str, Any]:
    """
    14개 에피소드에 30일치 예약 일정을 배정하고 CSV 및 JSON 매니페스트를 생성합니다.
    """
    output_dir = Path(output_dir)
    dates = generate_schedule_dates(count=len(episodes), start_date=start_date)
    
    csv_file = output_dir / "youtube_batch_schedule.csv"
    json_file = output_dir / "schedule_manifest.json"
    
    csv_rows = []
    
    for i, ep in enumerate(episodes):
        sched_dt = dates[i]
        # KST 및 UTC 포맷
        kst_str = sched_dt.strftime("%Y-%m-%d %H:%M KST")
        # YouTube Data API는 UTC ISO 8601 기준 필요 (KST는 UTC+9)
        utc_dt = sched_dt - timedelta(hours=9)
        utc_iso = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        ep["schedule"] = {
            "order": i + 1,
            "scheduled_kst": kst_str,
            "scheduled_utc_iso": utc_iso,
            "weekday_ko": ["월", "화", "수", "목", "금", "토", "일"][sched_dt.weekday()],
            "status": "Ready for Upload"
        }
        
        seo = ep.get("seo", {})
        title = seo.get("selected_title") or (seo.get("titles", ["신비한 건축사전"])[0])
        tags_str = seo.get("tags_string", "")
        desc = seo.get("description", "")
        pinned = seo.get("pinned_comment", "")
        final_video = ep.get("final_video", "")
        
        csv_rows.append({
            "No": i + 1,
            "요일": ep["schedule"]["weekday_ko"],
            "예약일시(KST)": kst_str,
            "YouTube_UTC_ISO": utc_iso,
            "영상제목": title,
            "비디오파일명": Path(final_video).name if final_video else f"episode_{i+1:02d}.mp4",
            "설명란": desc,
            "태그": tags_str,
            "고정댓글": pinned,
            "상태": "예약준비완료"
        })
        
    # CSV 저장 (Excel 및 한글 호환 UTF-8-SIG)
    fieldnames = ["No", "요일", "예약일시(KST)", "YouTube_UTC_ISO", "영상제목", "비디오파일명", "설명란", "태그", "고정댓글", "상태"]
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
        
    # JSON 매니페스트 저장
    manifest_data = {
        "generated_at": datetime.now().isoformat(),
        "total_episodes": len(episodes),
        "schedule_plan": "30일치 주 3회 (월/수/금 18:00)",
        "csv_manifest": str(csv_file),
        "episodes": episodes
    }
    json_file.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    logger.info(f"30일치 스케줄 매니페스트 생성 완료: {csv_file.name}, {json_file.name}")
    return manifest_data
