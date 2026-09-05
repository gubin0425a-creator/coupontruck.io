@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [쿠폰트럭] 자동 업데이트 실행 중: %date% %time%
python updater.py
echo [쿠폰트럭] 작업 완료.
