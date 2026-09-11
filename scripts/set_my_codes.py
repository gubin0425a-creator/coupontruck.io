#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
쿠폰트럭 (CouponTruck) - 사용자 전용 제휴/추천 코드 원클릭 일괄 치환 엔진
명령어 예시:
  python scripts/set_my_codes.py --brand gamsgo --code NEWCODE --url "https://www.gamsgo.com/partner/XXXXX"
  python scripts/set_my_codes.py --brand temu --code MYCODE --url "https://temu.to/k/XXXXX"
  python scripts/set_my_codes.py --brand iherb --code MYCODE
  python scripts/set_my_codes.py --brand klook --code MYCODE
  python scripts/set_my_codes.py --status  (현재 등록된 내 코드 현황 조회)
"""

import os
import re
import sys
import json
import argparse
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_BRANDS_DIR = os.path.join(BASE_DIR, "config", "brands")
DATA_COUPONS = os.path.join(BASE_DIR, "data", "coupons.json")
DATA_OFFERS = os.path.join(BASE_DIR, "data", "offers.json")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")
MAIN_JS = os.path.join(BASE_DIR, "main.js")

# 브랜드별 기본 식별 패턴
BRAND_DEFAULTS = {
    "gamsgo": {
        "name": "겜스고 (GamsGo)",
        "config": "gamsgo.json",
        "current_code": "DASSD",
        "current_url": "https://www.gamsgo.com/partner/aTqwg",
        "target_files": [INDEX_HTML, MAIN_JS, DATA_COUPONS, DATA_OFFERS]
    },
    "temu": {
        "name": "테무 (Temu)",
        "config": "temu.json",
        "current_code": "alu590849",
        "current_url": "https://temu.to/k/g1cxpg2jjge",
        "target_files": [DATA_COUPONS, DATA_OFFERS]
    },
    "iherb": {
        "name": "아이허브 (iHerb)",
        "config": "iherb.json",
        "current_code": "gubin0425a",
        "current_url": "https://kr.iherb.com/?rcode=gubin0425a",
        "target_files": [DATA_COUPONS, DATA_OFFERS]
    },
    "klook": {
        "name": "클룩 (Klook)",
        "config": "klook.json",
        "current_code": "GUHU8L",
        "current_url": "https://www.klook.com/ko/invite/GUHU8L?c=KRW",
        "target_files": [DATA_COUPONS, DATA_OFFERS]
    }
}


def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def get_current_info(brand_key):
    cfg_path = os.path.join(CONFIG_BRANDS_DIR, f"{brand_key}.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                mapping = d.get("affiliate_mapping", {})
                return {
                    "code": mapping.get("referral_code") or mapping.get("coupon_code", ""),
                    "url": mapping.get("tracking_url", "")
                }
        except Exception:
            pass
    defaults = BRAND_DEFAULTS.get(brand_key, {})
    return {
        "code": defaults.get("current_code", ""),
        "url": defaults.get("current_url", "")
    }


def update_brand(brand_key, new_code=None, new_url=None):
    brand_key = brand_key.lower().strip()
    if brand_key not in BRAND_DEFAULTS:
        print(f"❌ 지원되지 않는 브랜드입니다: {brand_key} (지원: {', '.join(BRAND_DEFAULTS.keys())})")
        return False

    info = BRAND_DEFAULTS[brand_key]
    current = get_current_info(brand_key)
    old_code = current["code"] or info["current_code"]
    old_url = current["url"] or info["current_url"]

    new_code = (new_code or "").strip()
    new_url = (new_url or "").strip()

    print(f"\n==================================================")
    print(f"🔄 [{info['name']}] 제휴 코드 및 링크 교체 시작")
    print(f"  - 기존 코드: {old_code} -> 신규: {new_code or '(유지)'}")
    print(f"  - 기존 링크: {old_url} -> 신규: {new_url or '(유지)'}")
    print(f"==================================================")

    # 1. config/brands/<brand>.json 업데이트
    cfg_file = os.path.join(CONFIG_BRANDS_DIR, info["config"])
    if os.path.exists(cfg_file):
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                cfg_data = json.load(f)
            if "affiliate_mapping" in cfg_data:
                if new_code:
                    if "referral_code" in cfg_data["affiliate_mapping"]:
                        cfg_data["affiliate_mapping"]["referral_code"] = new_code
                    if "coupon_code" in cfg_data["affiliate_mapping"]:
                        cfg_data["affiliate_mapping"]["coupon_code"] = new_code
                if new_url:
                    cfg_data["affiliate_mapping"]["tracking_url"] = new_url
            with open(cfg_file, "w", encoding="utf-8") as f:
                json.dump(cfg_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 설정 파일 업데이트 완료: {os.path.basename(cfg_file)}")
        except Exception as e:
            print(f"⚠️ 설정 파일 수정 오류: {e}")

    # 2. 관련 파일 전역 치환 (HTML, JS, JSON 등)
    modified_files_count = 0
    for file_path in info["target_files"]:
        if not os.path.exists(file_path):
            continue
        content = read_file(file_path)
        changed = False

        if new_url and old_url and old_url in content:
            content = content.replace(old_url, new_url)
            changed = True

        if new_code and old_code and old_code != new_code:
            # 특수 처리: 겜스고의 경우 HTML/JS 전역 치환
            if brand_key == "gamsgo":
                content = content.replace(old_code, new_code)
                changed = True
            else:
                # JSON 파일 내 해당 브랜드 항목만 안전 치환
                if file_path.endswith(".json"):
                    content = content.replace(f'"{old_code}"', f'"{new_code}"')
                    content = content.replace(f'[{old_code}]', f'[{new_code}]')
                    changed = True

        if changed:
            write_file(file_path, content)
            print(f"✅ 파일 내용 치환 완료: {os.path.basename(file_path)}")
            modified_files_count += 1

    # 3. 겜스고의 경우 index.html 특수 링크들 추가 확인
    if brand_key == "gamsgo" and new_url:
        index_content = read_file(INDEX_HTML)
        if "aTqwg" in index_content:
            new_partner_id = new_url.split("/")[-1]
            index_content = re.sub(r"https://www\.gamsgo\.com/partner/[A-Za-z0-9]+", new_url, index_content)
            write_file(INDEX_HTML, index_content)
            print("✅ index.html 겜스고 파트너 링크 전면 갱신 완료")

    print(f"\n🎉 [{info['name']}] 코드/링크 치환 작업이 성공적으로 완료되었습니다!")
    return True


def show_status():
    print("\n========================================================")
    print("📊 [쿠폰트럭] 현재 등록된 제휴 및 프로모션 코드 현황")
    print("========================================================")
    for k, v in BRAND_DEFAULTS.items():
        info = get_current_info(k)
        print(f"• {v['name']:<20}: 코드 [{info['code']}]")
        print(f"  링크: {info['url']}")
    print("========================================================\n")


def main():
    parser = argparse.ArgumentParser(description="쿠폰트럭 내 코드 원클릭 일괄 교체기")
    parser.add_argument("--brand", type=str, help="브랜드명 (gamsgo, temu, iherb, klook)")
    parser.add_argument("--code", type=str, help="새 프로모션/추천인 코드")
    parser.add_argument("--url", type=str, help="새 파트너/어필리에이트 링크")
    parser.add_argument("--status", action="store_true", help="현재 코드 현황 확인")

    args = parser.parse_args()

    if args.status or (not args.brand and not args.code and not args.url):
        show_status()
        return

    if not args.brand:
        print("❌ --brand 옵션이 필요합니다. (예: --brand gamsgo --code MYCODE)")
        return

    success = update_brand(args.brand, args.code, args.url)
    if success:
        print("⚡ 유효성 검사 및 정적 빌드 실행 중...")
        try:
            subprocess.run(["npm", "run", "build"], cwd=BASE_DIR, shell=True, check=True)
            print("✅ coupons.json 최신 빌드 동기화 완료!")
        except Exception as e:
            print(f"⚠️ 빌드 실행 알림: {e}")


if __name__ == "__main__":
    main()
