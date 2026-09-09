@echo off
chcp 65001 > nul
title WonkaShorts Studio - 원카 숏츠 스튜디오
echo ========================================================
echo   WonkaShorts Studio (원카 숏츠 스튜디오)
echo   신비한 건축사전 스타일 30일치 원클릭 풀 자동화 프로그램
echo   API 비용 0원 / SEO 100점 / 주 3회 자동 예약 시스템
echo ========================================================
echo.
echo 웹 대시보드를 로딩 중입니다. 잠시만 기다려주세요...
timeout /t 2 > nul
start "" "http://localhost:8520"
python -m uvicorn shorts_studio.web_app:app --host 127.0.0.1 --port 8520
pause
