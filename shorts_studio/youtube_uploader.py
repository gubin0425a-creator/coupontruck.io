# -*- coding: utf-8 -*-
"""
Google YouTube Data API v3 기반 숏폼 자동 예약 업로더
비공개(Private) 상태로 업로드 후 지정된 날짜/시간(월/수/금 18:00)에 자동 공개(Scheduled) 설정
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

CLIENT_SECRETS_FILE = Path(__file__).resolve().parent / "client_secrets.json"
TOKEN_FILE = Path(__file__).resolve().parent / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """
    Google OAuth 2.0 인증을 진행하고 YouTube API 클라이언트를 반환합니다.
    """
    if not CLIENT_SECRETS_FILE.exists():
        logger.warning("client_secrets.json 파일이 없습니다. 모의(Mock) 예약 모드로 작동합니다.")
        return None
        
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        creds = None
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
            
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        logger.error(f"YouTube 인증 실패: {e}")
        return None

def upload_and_schedule_video(
    video_path: Path,
    title: str,
    description: str,
    tags: list,
    publish_at_utc_iso: str,
    category_id: str = "28"
) -> Dict[str, Any]:
    """
    영상을 유튜브에 업로드하고 지정된 UTC ISO 시각에 예약 공개로 설정합니다.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return {"success": False, "error": f"비디오 파일 없음: {video_path}"}
        
    service = get_authenticated_service()
    
    # client_secrets.json이 없을 때의 안전한 시뮬레이션 응답
    if service is None:
        return {
            "success": True,
            "mode": "Simulation (client_secrets.json 대기)",
            "video_id": f"mock_{video_path.stem}",
            "title": title,
            "scheduled_time": publish_at_utc_iso,
            "notice": "YouTube API 키를 등록하면 즉시 채널로 실제 예약 업로드됩니다."
        }
        
    try:
        from googleapiclient.http import MediaFileUpload
        
        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:30],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_at_utc_iso,
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
        request = service.videos().insert(part="snippet,status", body=body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"업로드 진행률: {int(status.progress() * 100)}%")
                
        video_id = response.get("id")
        logger.info(f"YouTube 예약 업로드 성공! Video ID: {video_id}")
        return {
            "success": True,
            "video_id": video_id,
            "watch_url": f"https://youtube.com/shorts/{video_id}",
            "scheduled_time": publish_at_utc_iso
        }
    except Exception as e:
        logger.error(f"YouTube 예약 업로드 실패: {e}")
        return {"success": False, "error": str(e)}
