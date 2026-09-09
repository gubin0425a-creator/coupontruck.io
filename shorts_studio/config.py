import os
from pathlib import Path

# 기본 디렉터리 경로
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = ASSETS_DIR / "templates"
BGM_DIR = ASSETS_DIR / "bgm"
CACHE_DIR = ASSETS_DIR / "cache"
OUTPUT_DIR = BASE_DIR / "output"

for directory in [ASSETS_DIR, TEMPLATES_DIR, BGM_DIR, CACHE_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 비디오 렌더링 설정 (신비한 건축사전 숏폼 규격)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30

# 폰트 경로 (Windows 내장 맑은 고딕 볼드)
WINDOWS_FONT = "C:/Windows/Fonts/malgunbd.ttf"
FALLBACK_FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_PATH = WINDOWS_FONT if os.path.exists(WINDOWS_FONT) else FALLBACK_FONT

# Edge-TTS 추천 한국어 신경망 보이스
VOICE_OPTIONS = {
    "injoon": "ko-KR-InJoonNeural",  # 신비한 건축사전 스타일 (차분하고 신뢰감 있는 중저음 남성)
    "sunhi": "ko-KR-SunHiNeural",    # 명확하고 또렷한 여성
    "bongjin": "ko-KR-BongJinNeural", # 차분한 남성
    "hyunsu": "ko-KR-HyunsuNeural"   # 젊고 친근한 남성
}
DEFAULT_VOICE = VOICE_OPTIONS["injoon"]

# 30일치 스케줄링 설정 (주 3회: 월, 수, 금 18:00 KST)
SCHEDULE_DAYS_PER_WEEK = 3
DEFAULT_SCHEDULE_DAYS = ["Monday", "Wednesday", "Friday"] # 월, 수, 금
DEFAULT_PUBLISH_HOUR = 18 # 18:00 KST
DEFAULT_BATCH_COUNT = 14  # 1달(약 4.5주) 기준 14편

# Gemini API (선택사항, 없을 시 100% 무료 내장 지식 베이스 사용)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
