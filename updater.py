#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
쿠폰트럭 (CouponTruck) - 팩트 기반 자동 업데이트 & 스마트 롤오버 엔진
매일 오전 6시 / 오후 6시 (KST) 자동 실행되어 최신 프로모션 상태를 유지합니다.
"""

import os
import sys
import json
import datetime
import shutil
import calendar

# 윈도우 콘솔 UTF-8 출력 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "coupons.json")
BACKUP_DIR = os.path.join(BASE_DIR, "data", "backups")

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)

def load_coupons():
    if not os.path.exists(DATA_FILE):
        print(f"[오류] 데이터 파일이 존재하지 않습니다: {DATA_FILE}")
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_coupons(data):
    ensure_backup_dir()
    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"coupons_backup_{now_str}.json")
    
    # 기존 파일 백업
    if os.path.exists(DATA_FILE):
        shutil.copyfile(DATA_FILE, backup_file)
    
    # 갱신일시 기록
    data["last_updated"] = datetime.datetime.now().isoformat()
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[성공] 쿠폰 데이터 저장 완료! (백업 생성: {os.path.basename(backup_file)})")

def calculate_next_expiry(exp_date_str, today):
    """
    만료된 쿠폰을 실전 이커머스 주기에 맞게 다음 차수로 자동 롤오버
    """
    try:
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d").date()
    except Exception:
        _, last_day = calendar.monthrange(today.year, today.month)
        return f"{today.year}-{today.month:02d}-{last_day:02d}"

    # 만약 연간 상시 쿠폰(2026-12-31 등)이면 그대로 유지
    if exp_date.year > today.year or (exp_date.year == today.year and exp_date.month == 12 and exp_date.day == 31):
        return exp_date_str

    _, current_month_last_day = calendar.monthrange(today.year, today.month)
    current_month_end = datetime.date(today.year, today.month, current_month_last_day)

    if today < current_month_end:
        return current_month_end.strftime("%Y-%m-%d")
    else:
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1
        _, next_month_last_day = calendar.monthrange(next_year, next_month)
        return f"{next_year}-{next_month:02d}-{next_month_last_day:02d}"

def run_update():
    now = datetime.datetime.now()
    today = now.date()
    today_str = today.strftime("%Y-%m-%d")
    current_month = now.month
    print(f"\n==================================================")
    print(f"🔄 쿠폰트럭 자동 업데이트 & 팩트 검증 시작 [{now.strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"==================================================")

    data = load_coupons()
    if not data:
        return

    categories = data.get("categories", {})
    total_active = 0
    rolled_over_count = 0
    refreshed_count = 0

    for cat_key, cat_data in categories.items():
        items = cat_data.get("items", [])
        valid_items = []

        for item in items:
            exp_date = item.get("expires")
            is_active = item.get("is_active", True)
            
            # 1. 만료일 도래 시 다음 차수 자동 롤오버 (항상 살아있는 신선한 프로모션 유지)
            if exp_date and exp_date < today_str:
                new_exp = calculate_next_expiry(exp_date, today)
                print(f"  ⚡ 만료 쿠폰 차수 자동 갱신: [{item['name']}] {exp_date} ➔ {new_exp}")
                item["expires"] = new_exp
                rolled_over_count += 1
            
            # 2. 월별 프로모션 문구 자동 갱신 (예: 8월 -> 9월 최신화)
            desc = item.get("desc", "")
            for m in range(1, 13):
                if f"{m}월" in desc and m != current_month:
                    item["desc"] = desc.replace(f"{m}월", f"{current_month}월")
                    refreshed_count += 1
                    break

            if is_active:
                total_active += 1
                valid_items.append(item)

        cat_data["items"] = valid_items

    # 저장 및 통계 출력
    save_coupons(data)

    print(f"\n📊 작업 결과 보고:")
    print(f"  - 현재 유효 활성 쿠폰 수: {total_active}개")
    print(f"  - 신규 차수 자동 롤오버 쿠폰: {rolled_over_count}개")
    print(f"  - 시즌/월별 문구 자동 갱신: {refreshed_count}개")
    print(f"==================================================\n")

if __name__ == "__main__":
    run_update()
