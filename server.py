#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
쿠폰트럭 (CouponTruck) - 올인원 웹서버 & 정기 자동 스케줄러 (고보안 로컬 전용)
웹 서버(포트 8000) + 매일 오전 7시/오후 7시 자동 업데이트 + 실시간 쿠폰 저장 API 통합 엔진

[보안 강화 사항]
1. 127.0.0.1 루프백 고정: 외부 Wi-Fi/LAN/인터넷 접속 100% 원천 차단
2. Host & Origin 헤더 검증: 외부 웹사이트에서의 CSRF/위조 호출 방어
3. 백엔드 X-Admin-Token 검증: 관리자 마스터 토큰 없이는 추가/수정/삭제 절대 불가
"""

import os
import sys
import json
import time
import hashlib
import threading
import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
import updater

# 윈도우 UTF-8 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "coupons.json")
BIND_HOST = "127.0.0.1"  # 🔒 오직 내 PC(루프백)에서만 수신 (외부 IP 접근 원천 차단)
PORT = 8000

ADMIN_TOKEN_FILE = os.path.join(BASE_DIR, ".admin_token")

def get_configured_admin_tokens():
    tokens = set()
    env_token = os.environ.get("COUPONTRUCK_ADMIN_TOKEN")
    if env_token:
        tokens.add(env_token.strip())
    if os.path.exists(ADMIN_TOKEN_FILE):
        try:
            with open(ADMIN_TOKEN_FILE, "r", encoding="utf-8") as f:
                t = f.read().strip()
                if t:
                    tokens.add(t)
        except Exception:
            pass
    if not tokens:
        import secrets
        gen_token = secrets.token_hex(16)
        with open(ADMIN_TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(gen_token)
        tokens.add(gen_token)
        print(f"🔑 [보안] 새 로컬 관리자 토큰이 생성되어 .admin_token에 보관되었습니다: {gen_token}")
    return tokens


class CouponTruckHandler(SimpleHTTPRequestHandler):
    """정적 파일 서빙 + 쿠폰 관리 고보안 REST API 지원 핸들러"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        super().end_headers()

    def verify_admin_auth(self):
        """서버 측 마스터 인증 및 Origin 검증 (CSRF 및 외부 무단 호출 100% 방어)"""
        host = self.headers.get("Host", "")
        # 1. Host 검증 (외부 IP 또는 다른 도메인을 통한 접근 차단)
        allowed_hosts = ("localhost", "127.0.0.1", "localhost:8000", "127.0.0.1:8000")
        if host not in allowed_hosts and not any(host.startswith(h) for h in allowed_hosts):
            print(f"🚨 [보안 차단] 잘못된 Host 접근: {host}")
            return False

        # 2. Origin 검증 (외부 웹사이트에서의 fetch/XHR 위조 요청 원천 차단)
        origin = self.headers.get("Origin")
        if origin and not (origin.startswith("http://localhost:8000") or origin.startswith("http://127.0.0.1:8000")):
            print(f"🚨 [보안 차단] 비인가 Origin 요청 차단: {origin}")
            return False

        # 3. X-Admin-Token 헤더 검증
        token = self.headers.get("X-Admin-Token", "").strip()
        if not token:
            print("🚨 [보안 차단] 관리자 인증 토큰 누락")
            return False

        valid_tokens = get_configured_admin_tokens()
        if token in valid_tokens:
            return True

        print(f"🚨 [보안 차단] 유효하지 않은 관리자 토큰: {token[:8]}...")
        return False

    def do_GET(self):
        # /admin 또는 /admin/ 접속 시 관리자 전체 페이지로 리다이렉트
        if self.path in ("/admin", "/admin/"):
            self.send_response(302)
            self.send_header("Location", "/admin.html")
            self.end_headers()
            return

        # 쿠폰 데이터 API
        if self.path.startswith("/api/coupons"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b'{"error": "data not found"}')
            return
        
        # 시스템 상태 조회 API
        elif self.path.startswith("/api/status"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            status = {
                "server_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "schedule": "매일 07:00 / 19:00 자동 업데이트 가동 중",
                "bind_host": BIND_HOST,
                "port": PORT,
                "status": "online",
                "security": "127.0.0.1 loopback only + token guarded"
            }
            self.wfile.write(json.dumps(status, ensure_ascii=False).encode("utf-8"))
            return

        # 일반 정적 파일 서빙
        super().do_GET()

    def do_POST(self):
        # 관리자 토큰 검증 API (프론트엔드 연동)
        if self.path.startswith("/api/auth"):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                auth_data = json.loads(body)
                candidate_token = auth_data.get("token", "").strip()
                valid_tokens = get_configured_admin_tokens()
                if candidate_token and candidate_token in valid_tokens:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"authenticated": True}).encode("utf-8"))
                    return
            except Exception:
                pass
            self.send_response(401)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"authenticated": False, "error": "Invalid admin token"}).encode("utf-8"))
            return

        # 활성 상태 원클릭 토글 API
        if self.path.startswith("/api/coupons/toggle"):
            if not self.verify_admin_auth():
                self.send_response(403)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "Forbidden: Admin authentication required"}')
                return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                req_data = json.loads(body)
                target_code = req_data.get("code", "").strip().upper()
                target_id = req_data.get("id", "").strip()
                new_state = bool(req_data.get("is_active", True))

                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                found = False
                for cat in data["categories"].values():
                    for item in cat.get("items", []):
                        if (target_code and item.get("code", "").strip().upper() == target_code) or (target_id and item.get("id") == target_id):
                            item["is_active"] = new_state
                            found = True

                if found:
                    data["last_updated"] = datetime.datetime.now().isoformat()
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": found, "is_active": new_state}).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
                return

        # 일괄 작업 API (bulk delete / bulk status)
        if self.path.startswith("/api/coupons/bulk"):
            if not self.verify_admin_auth():
                self.send_response(403)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "Forbidden: Admin authentication required"}')
                return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                req_data = json.loads(body)
                action = req_data.get("action")
                codes = [c.strip().upper() for c in req_data.get("codes", []) if c]

                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                affected_count = 0
                if action == "delete":
                    for cat in data["categories"].values():
                        orig_len = len(cat["items"])
                        cat["items"] = [item for item in cat["items"] if item.get("code", "").strip().upper() not in codes]
                        affected_count += (orig_len - len(cat["items"]))
                elif action in ("activate", "deactivate"):
                    is_active = (action == "activate")
                    for cat in data["categories"].values():
                        for item in cat.get("items", []):
                            if item.get("code", "").strip().upper() in codes:
                                item["is_active"] = is_active
                                affected_count += 1

                if affected_count > 0:
                    data["last_updated"] = datetime.datetime.now().isoformat()
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "affected": affected_count}).encode("utf-8"))
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
                return

        # 전체 JSON 데이터 복원/가져오기 API
        if self.path.startswith("/api/coupons/import"):
            if not self.verify_admin_auth():
                self.send_response(403)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "Forbidden: Admin authentication required"}')
                return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                imported_data = json.loads(body)
                if "categories" in imported_data:
                    imported_data["last_updated"] = datetime.datetime.now().isoformat()
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(imported_data, f, ensure_ascii=False, indent=2)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "message": "데이터 복원 완료"}).encode("utf-8"))
                    return
                else:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "잘못된 데이터 구조 (categories 필드 필요)"}).encode("utf-8"))
                    return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
                return

        # 쿠폰 추가/수정 API
        if self.path.startswith("/api/coupons"):
            if not self.verify_admin_auth():
                self.send_response(403)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "Forbidden: Admin authentication required"}')
                return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                item_data = json.loads(body)
                cat_key = item_data.get("category", "shopping")
                
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 카테고리가 없는 경우 기본 생성
                if cat_key not in data["categories"]:
                    cat_titles = {
                        "travel": "✈️ 여행 · 항공권 · 호텔 숙소 할인코드",
                        "shopping": "🛍️ 종합쇼핑 · 직구 · 생활 커머스 할인코드",
                        "sub": "📺 OTT 스트리밍 · AI · VPN 구독 할인코드",
                        "fashion": "👗 패션 · 뷰티 · 명품 편집샵 할인코드",
                        "game": "🎮 게임 · 디지털 소프트웨어 프로모션",
                        "guide": "💡 스마트 쇼핑 실전 꿀팁 & 직구 절약 가이드"
                    }
                    data["categories"][cat_key] = {
                        "title": cat_titles.get(cat_key, f"📌 {cat_key} 혜택"),
                        "badge": "특가",
                        "items": []
                    }
                
                items = data["categories"][cat_key]["items"]
                target_code = item_data.get("code", "").strip()
                target_id = item_data.get("id")

                # 기존 항목 검색 (id 일치 우선, 그 후 code 일치)
                existing_idx = -1
                if target_id:
                    existing_idx = next((i for i, item in enumerate(items) if item.get("id") == target_id), -1)
                if existing_idx < 0 and target_code:
                    existing_idx = next((i for i, item in enumerate(items) if item.get("code", "").strip().upper() == target_code.upper()), -1)
                
                new_item = {
                    "id": target_id or f"{cat_key[:3]}-{int(time.time())}",
                    "name": item_data.get("name", "").strip(),
                    "code": target_code,
                    "desc": item_data.get("desc", "").strip(),
                    "url": item_data.get("url", "").strip(),
                    "expires": item_data.get("expires", "2026-12-31"),
                    "is_active": item_data.get("is_active", True),
                    "badge": item_data.get("badge", "NEW"),
                    "verified_at": item_data.get("verified_at", datetime.datetime.now().isoformat()),
                    "type": item_data.get("type", "COUPON")
                }
                
                if existing_idx >= 0:
                    items[existing_idx] = new_item
                else:
                    items.insert(0, new_item)
                    
                data["last_updated"] = datetime.datetime.now().isoformat()
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": "쿠폰 저장 완료", "item": new_item}).encode("utf-8"))
                print(f"⚡ [API] 쿠폰 등록/수정 완료: [{new_item['name']}] {new_item['code']}")
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
                return

        # 즉시 업데이트 트리거 API
        elif self.path.startswith("/api/run-update"):
            if not self.verify_admin_auth():
                self.send_response(403)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "Forbidden: Admin authentication required"}')
                return

            updater.run_update()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "자동 업데이트 및 만료 갱신 완료"}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_DELETE(self):
        # 쿠폰 삭제 API
        if self.path.startswith("/api/coupons"):
            if not self.verify_admin_auth():
                self.send_response(403)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b'{"error": "Forbidden: Admin authentication required"}')
                return

            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            code = query.get("code", [None])[0]
            target_id = query.get("id", [None])[0]
            
            if code or target_id:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                deleted = False
                for cat in data["categories"].values():
                    orig_len = len(cat["items"])
                    cat["items"] = [
                        item for item in cat["items"]
                        if not (
                            (code and item.get("code", "").strip().upper() == code.strip().upper()) or
                            (target_id and item.get("id") == target_id)
                        )
                    ]
                    if len(cat["items"]) < orig_len:
                        deleted = True
                
                if deleted:
                    data["last_updated"] = datetime.datetime.now().isoformat()
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"🗑️ [API] 쿠폰 코드 삭제 완료: {code}")

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": deleted}).encode("utf-8"))
                return

        self.send_response(404)
        self.end_headers()


def run_scheduler_loop():
    """매일 오전 7시 / 오후 7시 자동 업데이트 백그라운드 워커"""
    print("⏰ [스케줄러] 매일 오전 07:00 / 오후 19:00 자동 업데이트 타이머 가동 시작")
    last_triggered_date_hour = None

    while True:
        try:
            now = datetime.datetime.now()
            current_date_hour = now.strftime("%Y-%m-%d_%H")
            
            # 07시 또는 19시 정각 체크 (시간당 1회만 트리거)
            if now.hour in (7, 19) and current_date_hour != last_triggered_date_hour:
                print(f"\n🔔 [정기 스케줄 트리거] {now.strftime('%Y-%m-%d %H:%M:%S')} - updater.py 자동 실행!")
                updater.run_update()
                last_triggered_date_hour = current_date_hour
        except Exception as e:
            print(f"❌ [스케줄러 오류] {e}")

        # 15초마다 시간 체크
        time.sleep(15)


def start_server():
    server_address = (BIND_HOST, PORT)
    httpd = HTTPServer(server_address, CouponTruckHandler)
    
    # 1. 백그라운드 스케줄러 스레드 시작
    scheduler_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
    scheduler_thread.start()

    print(f"\n========================================================")
    print(f"🚀 [쿠폰트럭 고보안 로컬 서버] 정상 구동 완료!")
    print(f"🌐 접속 주소: http://{BIND_HOST}:{PORT} (http://localhost:{PORT})")
    print(f"🔒 보안 모드: 127.0.0.1 루프백 고정 (외부 Wi-Fi/인터넷 접근 100% 원천 차단)")
    print(f"🔑 API 보호: 마스터 토큰 헤더(X-Admin-Token) 검증 활성화")
    print(f"⏰ 자동 업데이트: 매일 오전 07:00, 오후 19:00 자동 실행")
    print(f"========================================================\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
