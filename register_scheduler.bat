@echo off
chcp 65001 >nul
echo ==============================================================
echo [쿠폰트럭] 윈도우 작업 스케줄러 자동 등록 (매일 오전 7시 / 오후 7시)
echo ==============================================================

set BAT_PATH=%~dp0run_update.bat

echo 1. 오전 07:00 작업 등록 중...
schtasks /create /tn "CouponTruck_Update_07AM" /tr "\"%BAT_PATH%\"" /sc daily /st 07:00 /f

echo 2. 오후 19:00 작업 등록 중...
schtasks /create /tn "CouponTruck_Update_07PM" /tr "\"%BAT_PATH%\"" /sc daily /st 19:00 /f

echo.
echo ==============================================================
echo [완료] 매일 오전 7시와 오후 7시에 updater.py가 자동 실행됩니다!
echo ==============================================================
pause
