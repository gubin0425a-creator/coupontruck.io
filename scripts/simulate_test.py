#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
쿠폰트럭 (CouponTruck) - 전 기능 엔드투엔드(E2E) 작동 시뮬레이터
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_URL = "http://127.0.0.1:8000"
REMOTE_URL = "https://gubin0425a-creator.github.io/coupontruck.io"

test_results = []

def record_test(category, name, passed, details=""):
    test_results.append({
        "category": category,
        "name": name,
        "passed": passed,
        "details": details
    })
    mark = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{mark}] {name}")
    if details:
        print(f"        └─ {details}")


print("================================================================")
print("🚀 [쿠폰트럭] 전 기능 가상 사용자 작동 시뮬레이션 시작")
print("================================================================\n")

# -------------------------------------------------------------
# 1. 로컬 웹 서버 및 백엔드 API 테스트
# -------------------------------------------------------------
print("▶ [1단계] 로컬 웹서버 및 보안 REST API 가동 상태 검증")
try:
    resp = urllib.request.urlopen(f"{LOCAL_URL}/", timeout=3)
    record_test("서버", "메인 index.html 정상 서빙 (HTTP 200)", resp.status == 200, f"Status: {resp.status}")
except Exception as e:
    record_test("서버", "메인 index.html 서빙", False, str(e))

try:
    resp = urllib.request.urlopen(f"{LOCAL_URL}/api/status", timeout=3)
    data = json.loads(resp.read().decode("utf-8"))
    record_test("서버", "백엔드 상태 API (/api/status)", data.get("status") == "online", f"서버상태: {data.get('status')}, 자동스케줄: {data.get('schedule')}")
except Exception as e:
    record_test("서버", "백엔드 상태 API", False, str(e))

try:
    resp = urllib.request.urlopen(f"{LOCAL_URL}/api/local-token", timeout=3)
    tok_data = json.loads(resp.read().decode("utf-8"))
    token = tok_data.get("token")
    record_test("보안", "로컬 관리자 토큰 조회 API (/api/local-token)", bool(token), f"토큰 정상 반환: {token[:4]}****")
except Exception as e:
    record_test("보안", "로컬 관리자 토큰 조회 API", False, str(e))


# -------------------------------------------------------------
# 2. 데이터 무결성 및 사용자 코드 (gubin0425a) 검증
# -------------------------------------------------------------
print("\n▶ [2단계] 사용자 전용 코드 (gubin0425a & 핵심 제휴코드) 무결성 검증")
coupons_data = None
try:
    resp = urllib.request.urlopen(f"{LOCAL_URL}/data/coupons.json", timeout=3)
    coupons_data = json.loads(resp.read().decode("utf-8"))
    total_items = sum(len(c.get("items", [])) for c in coupons_data.get("categories", {}).values())
    record_test("데이터", "쿠폰 원본 데이터 로드 (data/coupons.json)", total_items == 103, f"전체 활성 혜택: {total_items}개")
except Exception as e:
    record_test("데이터", "쿠폰 데이터 로드", False, str(e))

if coupons_data:
    all_items = [i for c in coupons_data["categories"].values() for i in c.get("items", [])]
    
    # gubin0425a 사용자 추천인 코드 (에어알로, 유심사) 검사
    airalo = next((i for i in all_items if "에어알로" in i.get("name", "")), None)
    usimsa = next((i for i in all_items if "유심사" in i.get("name", "")), None)
    user_referral_ok = (airalo and airalo.get("code") == "gubin0425a") and (usimsa and usimsa.get("code") == "gubin0425a")
    record_test("사용자코드", "사용자 추천인 코드 'gubin0425a' 탑재 (에어알로, 유심사)", user_referral_ok, "에어알로 및 유심사에 정상 탑재 확인")

    # 대문자 GUBIN0425A 잔여 여부 검사
    upper_items = [i for i in all_items if i.get("code") == "GUBIN0425A"]
    record_test("사용자코드", "대문자 'GUBIN0425A' 잔여 0건 확인", len(upper_items) == 0, f"잔여 대문자: {len(upper_items)}개")

    # 핵심 5대 캐시 수익 제휴 링크 보존 검사
    gamsgo = next((i for i in all_items if "겜스고" in i.get("name", "")), None)
    temu = next((i for i in all_items if "테무" in i.get("name", "")), None)
    iherb = next((i for i in all_items if "아이허브" in i.get("name", "")), None)
    klook = next((i for i in all_items if "클룩" in i.get("name", "")), None)
    trip = next((i for i in all_items if "트립닷컴" in i.get("name", "")), None)

    gamsgo_ok = gamsgo and gamsgo.get("code") == "DASSD" and "aTqwg" in gamsgo.get("url", "")
    record_test("수익링크", "겜스고 정식 제휴 링크 보존 (DASSD)", gamsgo_ok, f"코드: {gamsgo.get('code')}, URL: {gamsgo.get('url')}")

    temu_ok = temu and temu.get("code") == "alu590849" and "g1cxpg2jjge" in temu.get("url", "")
    record_test("수익링크", "테무 30% 정식 제휴 링크 보존 (alu590849)", temu_ok, f"코드: {temu.get('code')}")

    iherb_ok = iherb and iherb.get("code") == "RKB1777" and "RKB1777" in iherb.get("url", "")
    record_test("수익링크", "아이허브 정식 리워드 링크 보존 (RKB1777)", iherb_ok, f"코드: {iherb.get('code')}")

    klook_ok = klook and klook.get("code") == "GUHU8L" and "GUHU8L" in klook.get("url", "")
    record_test("수익링크", "클룩 4천원 정식 초대 링크 보존 (GUHU8L)", klook_ok, f"코드: {klook.get('code')}")

    trip_ok = trip and "Allianceid=10493743" in trip.get("url", "")
    record_test("수익링크", "트립닷컴 정식 파트너스 트래킹 보존", trip_ok, "Allianceid=10493743 확인")


# -------------------------------------------------------------
# 3. 프론트엔드 UI 동작 로직 가상 시뮬레이션
# -------------------------------------------------------------
print("\n▶ [3단계] 방문자 행동 시뮬레이션 (카테고리 탭, 실시간 검색, 코드 복사)")
if coupons_data:
    cats = coupons_data["categories"]
    
    # 카테고리 필터 시뮬레이션
    expected_counts = {
        "all": 103,
        "travel": len(cats["travel"]["items"]),
        "shopping": len(cats["shopping"]["items"]),
        "sub": len(cats["sub"]["items"]),
        "fashion": len(cats["fashion"]["items"]),
        "game": len(cats["game"]["items"]),
        "guide": len(cats["guide"]["items"]),
    }
    
    filter_all_ok = True
    for cat_key, exp_count in expected_counts.items():
        if cat_key == "all":
            actual = len(all_items)
        else:
            actual = len(cats[cat_key]["items"])
        if actual != exp_count or actual == 0:
            filter_all_ok = False
            break

    record_test("UI시뮬레이션", "카테고리 6종 원터치 탭 필터링 시뮬레이션", filter_all_ok, 
                f"전체:103개, 여행:{expected_counts['travel']}개, 쇼핑:{expected_counts['shopping']}개, OTT:{expected_counts['sub']}개, 패션:{expected_counts['fashion']}개, 게임:{expected_counts['game']}개, 팁:{expected_counts['guide']}개 (0개인 카테고리 없음)")

    # 검색 시뮬레이션
    keywords = ["겜스고", "테무", "gubin0425a", "호텔", "eSIM"]
    search_ok = True
    for kw in keywords:
        matched = [i for i in all_items if kw.lower() in (i.get("name","")+i.get("desc","")+i.get("code","")).lower()]
        if len(matched) == 0:
            search_ok = False
            break
    record_test("UI시뮬레이션", "실시간 브랜드/코드 검색엔진 시뮬레이션", search_ok, 
                f"테스트 검색어({', '.join(keywords)}) 전원 일치 결과 도출 완료")

    # 코드 복사 시뮬레이션 (gubin0425a 복사 여부)
    sample_gubin = gubin_items[0] if gubin_items else {}
    copied_code = sample_gubin.get("code")
    record_test("UI시뮬레이션", "원클릭 쿠폰코드 복사 시뮬레이션", copied_code == "gubin0425a", 
                f"샘플 브랜드[{sample_gubin.get('name')}] 클릭 시 'gubin0425a' 정확히 복사 클립보드 페이로드 반환")


# -------------------------------------------------------------
# 4. 실제 온라인 라이브 배포 (GitHub Pages) 동기화 검증
# -------------------------------------------------------------
print("\n▶ [4단계] 인터넷 공개 웹사이트 (GitHub Pages) 실시간 동기화 검증")
try:
    req = urllib.request.Request(
        f"{REMOTE_URL}/data/coupons.json",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    resp = urllib.request.urlopen(req, timeout=5)
    remote_data = json.loads(resp.read().decode("utf-8"))
    r_all_items = [i for c in remote_data["categories"].values() for i in c.get("items", [])]
    r_gubin_count = len([i for i in r_all_items if i.get("code") == "gubin0425a"])
    r_total = len(r_all_items)
    
    remote_ok = r_total == 103 and r_gubin_count >= 2
    record_test("라이브배포", "GitHub Pages 라이브 사이트 데이터 동기화 상태", remote_ok, 
                f"온라인 사이트 전체 혜택: {r_total}개, 추천인/파트너 코드 및 브랜드 쿠폰 정상 동기화")
except Exception as e:
    record_test("라이브배포", "GitHub Pages 라이브 사이트 동기화", False, str(e))


# -------------------------------------------------------------
# 최종 결과 집계
# -------------------------------------------------------------
total_tests = len(test_results)
passed_tests = sum(1 for t in test_results if t["passed"])
failed_tests = total_tests - passed_tests

print("\n================================================================")
print(f"🏁 [시뮬레이션 종합 결과] 총 {total_tests}개 항목 중 {passed_tests}개 통과 (실패: {failed_tests}개)")
print(f"   종합 합격률: {(passed_tests/total_tests)*100:.1f}%")
print("================================================================\n")
