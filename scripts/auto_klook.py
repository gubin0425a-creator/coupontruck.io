import os
import sys
import time
import json
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "coupons.json")
OFFERS_FILE = os.path.join(BASE_DIR, "data", "offers.json")

def update_klook_in_db(code, invite_url):
    print(f"\n🎉 [자동 감지 성공] 클룩 추천코드 추출 완료: {code} | {invite_url}")
    
    # Update coupons.json
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        found = False
        for item in data["categories"]["travel"]["items"]:
            if item["id"] == "trv-03" or "클룩" in item["name"] or "Klook" in item["name"]:
                item["code"] = code
                item["url"] = invite_url or f"https://www.klook.com/ko/invite/{code}"
                item["badge"] = "5,000원 할인"
                item["is_active"] = True
                item["expires"] = "2026-12-31"
                found = True
                break
        
        if found:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ data/coupons.json 클룩 사장님 전용 코드로 업데이트 완료!")

    # Update offers.json
    if os.path.exists(OFFERS_FILE):
        with open(OFFERS_FILE, "r", encoding="utf-8") as f:
            offers = json.load(f)
        
        for o in offers:
            if o.get("id") == "trv-03" or "클룩" in o.get("title", "") or "Klook" in o.get("title", ""):
                o["coupon_code"] = code
                o["target_url"] = invite_url or f"https://www.klook.com/ko/invite/{code}"
                o["affiliate_url"] = invite_url or f"https://www.klook.com/ko/invite/{code}"
                o["end_date"] = "2026-12-31"
                o["badge"] = "5,000원 할인"
                break
        
        with open(OFFERS_FILE, "w", encoding="utf-8") as f:
            json.dump(offers, f, ensure_ascii=False, indent=2)
        print("✅ data/offers.json 클룩 사장님 전용 코드로 업데이트 완료!")

def main():
    active_port_file = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\DevToolsActivePort")
    if not os.path.exists(active_port_file):
        print("DevToolsActivePort not found")
        return

    with open(active_port_file, "r") as f:
        lines = [l.strip() for l in f]
    port, path = lines[0], lines[1]
    ws_endpoint = f"ws://127.0.0.1:{port}{path}"

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_endpoint)
        context = browser.contexts[0]
        
        klook_page = None
        for page in context.pages:
            if "klook.com" in page.url:
                klook_page = page
                break
        
        if not klook_page:
            klook_page = context.new_page()
            klook_page.goto("https://www.klook.com/ko/invite/", wait_until="domcontentloaded")

        print("🔍 클룩 탭 모니터링 시작... (로그인 완료 대기 중)")
        
        for attempt in range(60): # 3분간 감시
            try:
                url = klook_page.url
                # Check if logged in (not in /signin/)
                if "signin" not in url:
                    # We are in logged-in area! Try to extract code or invite link
                    text = klook_page.content()
                    
                    # Pattern 1: look for invite code (alphanumeric 5-10 chars like KLOOKXXXX, or code patterns)
                    code_match = re.search(r'invite/([A-Z0-9]{5,10})', text)
                    if not code_match:
                        code_match = re.search(r'code=([A-Z0-9]{5,10})', text)
                    if not code_match:
                        # Search for referral code container
                        elem = klook_page.locator('.invite-code, [data-testid="invite-code"], input[readonly]').first
                        if elem.count() > 0:
                            val = elem.input_value() or elem.inner_text()
                            if val and len(val.strip()) >= 4:
                                update_klook_in_db(val.strip(), f"https://www.klook.com/ko/invite/{val.strip()}")
                                return
                    
                    if code_match:
                        code = code_match.group(1)
                        update_klook_in_db(code, f"https://www.klook.com/ko/invite/{code}")
                        return
                    
                    # If on invite page, try to see if there's any invite button or text
                    klook_page.goto("https://www.klook.com/ko/invite/", wait_until="networkidle")
                    time.sleep(2)
                    
                    # Retry extraction
                    text2 = klook_page.content()
                    code_match2 = re.search(r'([A-Z0-9]{5,8})', text2)
                    # check links
                    links = klook_page.locator('a[href*="invite"]').all()
                    for l in links:
                        href = l.get_attribute("href") or ""
                        if "/invite/" in href and not href.endswith("/invite/"):
                            code = href.split("/invite/")[1].split("?")[0].strip()
                            if code:
                                update_klook_in_db(code, href)
                                return
            except Exception as e:
                pass
            time.sleep(3)
        
        print("시간 초과: 로그인이 완료되지 않았습니다.")

if __name__ == "__main__":
    main()
