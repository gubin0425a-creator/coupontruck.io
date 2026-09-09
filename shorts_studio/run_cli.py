# -*- coding: utf-8 -*-
"""
Shorts Studio 터미널/CLI 실행기
사용법: python -m shorts_studio.run_cli --count 14 --theme "신비한 세계 건축과 토목의 비밀"
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shorts_studio.pipeline import run_batch_pipeline
from shorts_studio.config import DEFAULT_BATCH_COUNT, DEFAULT_VOICE

def main():
    parser = argparse.ArgumentParser(description="WonkaShorts Studio CLI 숏폼 일괄 생성기")
    parser.add_argument("--count", type=int, default=DEFAULT_BATCH_COUNT, help="제작할 에피소드 수 (기본 14편)")
    parser.add_argument("--theme", type=str, default="신비한 세계 건축과 토목의 비밀", help="숏폼 주제 테마")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="나레이션 보이스 (기본 ko-KR-InJoonNeural)")
    parser.add_argument("--api-key", type=str, default=None, help="Gemini API 키 (선택사항)")

    args = parser.parse_args()
    print(f"=== [WonkaShorts Studio] {args.count}편 일괄 제작 시작 ===")
    print(f"테마: {args.theme}")
    print(f"보이스: {args.voice}")
    
    manifest = asyncio.run(run_batch_pipeline(
        theme=args.theme,
        count=args.count,
        voice=args.voice,
        api_key=args.api_key
    ))
    
    print("\n🎉 모든 작업이 성공적으로 완료되었습니다!")
    print(f"결과물 폴더: {manifest.get('csv_manifest')}")

if __name__ == "__main__":
    main()
