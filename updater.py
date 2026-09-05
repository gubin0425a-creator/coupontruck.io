#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
쿠폰트럭 (CouponTruck) - 자동 업데이트 & 만료 쿠폰 정리 스크립트
매일 오전 7시 / 오후 7시 자동 실행되도록 스케줄링됩니다.
"""

import os
import sys
import json
import datetime
import shutil

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

def run_update():
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_month = now.month
    print(f"\n==================================================")
    print(f"🔄 쿠폰트럭 자동 업데이트 작업 시작 [{now.strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"==================================================")

    data = load_coupons()
    if not data:
        return

    categories = data.get("categories", {})
    total_active = 0
    expired_removed = 0
    refreshed_count = 0

    for cat_key, cat_data in categories.items():
        items = cat_data.get("items", [])
        valid_items = []

        for item in items:
            exp_date = item.get("expires")
            is_active = item.get("is_active", True)
            
            # 1. 만료일 검사 (만료일이 지났으면 자동 제외/삭제)
            if exp_date and exp_date < today_str:
                print(f"  ❌ 만료 쿠폰 삭제: [{item['name']}] 코드: {item['code']} (만료일: {exp_date})")
                expired_removed += 1
                continue
            
            # 2. 월별 프로모션 문구 자동 갱신 (예: 2월 -> 3월 최신화)
            desc = item.get("desc", "")
            # 이전 달 문구가 들어있는 경우 최신 달로 자동 교체
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
    print(f"  - 기간 만료 자동 삭제 쿠폰: {expired_removed}개")
    print(f"  - 시즌/월별 문구 자동 갱신: {refreshed_count}개")
    print(f"==================================================\n")

if __name__ == "__main__":
    run_update()
