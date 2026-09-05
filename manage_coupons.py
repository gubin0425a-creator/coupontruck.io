#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
쿠폰 즉시 추가/삭제/수정 관리자 CLI 도구
사용법:
  - 목록 보기: python manage_coupons.py list [카테고리]
  - 쿠폰 추가: python manage_coupons.py add <카테고리> <브랜드명> <쿠폰코드> <설명> <링크> [만료일 YYYY-MM-DD] [배지]
  - 쿠폰 삭제: python manage_coupons.py delete <쿠폰코드>
  - 즉시 갱신: python manage_coupons.py run-update
"""

import sys
import os
import json
import uuid
import datetime

# 윈도우 콘솔 UTF-8 출력 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "coupons.json")

def load_data():
    if not os.path.exists(DATA_FILE):
        print(f"[오류] 데이터 파일 없음: {DATA_FILE}")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    data["last_updated"] = datetime.datetime.now().isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def list_coupons(target_cat=None):
    data = load_data()
    categories = data.get("categories", {})
    
    print("\n📋 [쿠폰트럭 전체 쿠폰 목록]")
    for cat_key, cat in categories.items():
        if target_cat and target_cat != cat_key:
            continue
        print(f"\n📂 [{cat_key}] {cat.get('title')}")
        items = cat.get("items", [])
        if not items:
            print("   (등록된 쿠폰 없음)")
        for idx, item in enumerate(items, 1):
            badge = f"[{item.get('badge')}] " if item.get("badge") else ""
            print(f"   {idx}. {item['name']} | 코드: {item['code']} | {badge}{item['desc']} (만료: {item.get('expires', '무기한')})")
    print("\n")

def add_coupon(cat_key, name, code, desc, url, expires="2026-12-31", badge=None):
    data = load_data()
    categories = data.get("categories", {})
    
    if cat_key not in categories:
        print(f"[오류] 잘못된 카테고리입니다. 가능한 카테고리: {list(categories.keys())}")
        return

    # 이미 존재하는 코드인지 확인
    for item in categories[cat_key]["items"]:
        if item["code"].upper() == code.upper():
            print(f"[알림] 이미 존재하는 쿠폰 코드입니다 ({code}). 기존 정보를 업데이트합니다.")
            item["name"] = name
            item["desc"] = desc
            item["url"] = url
            item["expires"] = expires
            item["badge"] = badge
            save_data(data)
            print(f"✅ [{name}] 쿠폰 수정 완료!")
            return

    new_item = {
        "id": f"{cat_key[:3]}-{uuid.uuid4().hex[:4]}",
        "name": name,
        "code": code.strip(),
        "desc": desc.strip(),
        "url": url.strip(),
        "expires": expires.strip(),
        "is_active": True,
        "badge": badge
    }
    categories[cat_key]["items"].insert(0, new_item)
    save_data(data)
    print(f"✅ [{name}] 신규 쿠폰 등록 완료! (코드: {code}, 카테고리: {cat_key})")

def delete_coupon(target_code):
    data = load_data()
    categories = data.get("categories", {})
    found = False

    for cat_key, cat in categories.items():
        items = cat.get("items", [])
        new_items = []
        for item in items:
            if item["code"].strip().upper() == target_code.strip().upper():
                found = True
                print(f"🗑️ 쿠폰 삭제됨: [{item['name']}] 코드: {item['code']} (카테고리: {cat_key})")
            else:
                new_items.append(item)
        cat["items"] = new_items

    if found:
        save_data(data)
        print("✅ 삭제 완료 및 데이터 갱신되었습니다.")
    else:
        print(f"❌ 코드 '{target_code}'를 찾을 수 없습니다.")

def print_help():
    print("""
[쿠폰트럭 관리자 도구 사용법]
1. 쿠폰 목록 보기:
   python manage_coupons.py list
   python manage_coupons.py list travel

2. 쿠폰 즉시 추가:
   python manage_coupons.py add travel "아고다" "AGODA05" "전객실 5% 할인" "https://agoda.com" 2026-12-31 "7%할인"

3. 쿠폰 즉시 삭제:
   python manage_coupons.py delete AGODA05

4. 만료 쿠폰 자동 정리 & 갱신:
   python manage_coupons.py run-update
""")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ["-h", "--help", "help"]:
        print_help()
        sys.exit(0)

    cmd = args[0].lower()
    if cmd == "list":
        cat = args[1] if len(args) > 1 else None
        list_coupons(cat)
    elif cmd == "add":
        if len(args) < 6:
            print("[오류] 매개변수가 부족합니다. 예: python manage_coupons.py add <카테고리> <브랜드> <코드> <설명> <링크> [만료일] [배지]")
            sys.exit(1)
        cat_key = args[1]
        name = args[2]
        code = args[3]
        desc = args[4]
        url = args[5]
        expires = args[6] if len(args) > 6 else "2026-12-31"
        badge = args[7] if len(args) > 7 else None
        add_coupon(cat_key, name, code, desc, url, expires, badge)
    elif cmd == "delete":
        if len(args) < 2:
            print("[오류] 삭제할 쿠폰 코드를 입력하세요. 예: python manage_coupons.py delete AGODA05")
            sys.exit(1)
        delete_coupon(args[1])
    elif cmd in ["run-update", "update"]:
        import updater
        updater.run_update()
    else:
        print(f"[오류] 알 수 없는 명령어: {cmd}")
        print_help()
